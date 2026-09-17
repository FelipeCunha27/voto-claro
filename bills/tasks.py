from django.tasks import task
from bills.models import Submission, AccessibleVersion, Bill
from bills.adapters.openai_adapter import generate_accessible_version, TransientGenerationError, PermanentGenerationError
from django.db import transaction

@task()
def generate_accessible_version_task(submission_id):
    submission = Submission.objects.get(id=submission_id)
    submission.status = Submission.Status.PROCESSING
    submission.save(update_fields=['status'])
    
    themes = [] # fetch themes if available
    
    try:
        result = generate_accessible_version(submission.source_text, themes)
        
        if not result.is_legislative_text:
            submission.status = Submission.Status.REJECTED
            submission.rejection_reason = "O texto enviado não parece ser um projeto de lei válido."
            submission.save()
            return
            
        with transaction.atomic():
            bill = submission.bill
            if not bill:
                bill = Bill.objects.create(
                    title=submission.title,
                    origin_body=submission.origin_body,
                    bill_number=submission.bill_number,
                    bill_year=submission.bill_year,
                    official_source_url=submission.official_source_url
                )
                submission.bill = bill
                
            version_number = AccessibleVersion.objects.filter(bill=bill).count() + 1
            AccessibleVersion.objects.create(
                bill=bill,
                submission=submission,
                version_number=version_number,
                summary=result.summary,
                who_is_affected=result.who_is_affected,
                practical_changes=result.practical_changes,
                points_of_attention=result.points_of_attention,
                generator_reference="gpt-4o-2024-08-06",
            )
            submission.status = Submission.Status.GENERATED
            submission.save()
            
    except TransientGenerationError as e:
        submission.attempt_count += 1
        if submission.attempt_count >= 3:
            submission.status = Submission.Status.FAILED
            submission.failure_reason = f"Falha temporária persistente: {str(e)}"
        else:
            submission.status = Submission.Status.RECEIVED
        submission.save()
    except PermanentGenerationError as e:
        submission.status = Submission.Status.FAILED
        submission.failure_reason = f"Erro permanente na geração: {str(e)}"
        submission.save()
