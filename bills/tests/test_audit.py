from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
# Model não existe ainda, vai falhar no import (Fase Red perfeita)
from bills.models import AuditEntry

User = get_user_model()

class TestAuditEntryAppendOnly(TestCase):

    def setUp(self):
        self.curator_user = User.objects.create_user(username="curator_audit", password="password")
        # Simulando is_curator, se o modelo base permitir
        setattr(self.curator_user, 'is_curator', True)

    def test_audit_entry_creation_success(self):
        """Verify that an AuditEntry can be successfully created."""
        entry = AuditEntry.objects.create(
            action='approve',
            actor=self.curator_user,
            reason="All good"
        )
        self.assertIsNotNone(entry.id)
        self.assertEqual(entry.action, 'approve')

    def test_audit_entry_cannot_be_deleted(self):
        """Verify that an existing AuditEntry cannot be deleted."""
        entry = AuditEntry.objects.create(
            action='reject',
            actor=self.curator_user,
            reason="Bad formatting"
        )
        
        with self.assertRaises(Exception):
            entry.delete()
        
        self.assertTrue(AuditEntry.objects.filter(id=entry.id).exists())

    def test_audit_entry_cannot_be_updated(self):
        """Verify that an existing AuditEntry cannot be modified (updated)."""
        entry = AuditEntry.objects.create(
            action='approve',
            actor=self.curator_user,
            reason="Initial reason"
        )
        
        entry.reason = "Modified reason"
        
        with self.assertRaises(Exception):
            entry.save()
            
        entry.refresh_from_db()
        self.assertEqual(entry.reason, "Initial reason")
