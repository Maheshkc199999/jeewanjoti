from django.db import models
from django.utils.timezone import now
from jeewanjyoti_user.models import CustomUser

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='appointments_as_doctor')
    appointment_date = models.DateTimeField(db_index=True)
    appointment_time = models.TimeField(null=True, blank=True)
    is_immediate = models.BooleanField(default=False)
    user_report = models.FileField(upload_to='reports/%(user_id)s/', null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    problem_description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Payment Fields
    invoice_no = models.CharField(max_length=20, unique=True, editable=False, blank=True)
    is_paid = models.BooleanField(default=False)  # Track payment status
    payment_token = models.CharField(max_length=100, null=True, blank=True)  # Store Khalti token
    amount = models.IntegerField(null=True, blank=True)  # Store the amount paid

    def save(self, *args, **kwargs):
        """Generate invoice number only after the instance has an ID."""
        if not self.invoice_no:
            super().save(*args, **kwargs)  # Save first to generate an ID
            date_str = now().strftime("%Y%m%d")  
            self.invoice_no = f"INV-{date_str}-{self.id:06d}"
            self.save(update_fields=['invoice_no'])  # Save only the invoice_no field
        else:
            super().save(*args, **kwargs)  # Save normally for updates


    def __str__(self):
        return f"Appointment {self.invoice_no} - Dr. {self.doctor.first_name} - {self.appointment_date}"

    class Meta:
        ordering = ['-appointment_date']
