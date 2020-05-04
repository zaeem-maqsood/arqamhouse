import decimal
from django.db import models
from houses.models import House
from django.utils import timezone
from django.db.models.signals import pre_save, post_save
from django.urls import reverse

# Create your models here.


def validate_file_extension(value):
    import os
    from django.core.exceptions import ValidationError
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.png', '.xlsx', '.xls']
    if not ext.lower() in valid_extensions:
        raise ValidationError(u'Unsupported file extension.')


def official_document_location(instance, filename):
    return "bank_direct_deposit_forms/%s/%s" % (instance.house.slug, instance.id)


class PayoutSetting(models.Model):
    name = models.CharField(max_length=150, null=False, blank=False)
    house = models.ForeignKey(House, on_delete=models.CASCADE, blank=False, null=False)
    transit = models.CharField(max_length=5, blank=False, null=False)
    institution = models.CharField(max_length=3, null=False, blank=False)
    account = models.CharField(max_length=12, null=False, blank=False)
    official_document = models.FileField(upload_to=official_document_location, blank=True, null=True, validators=[validate_file_extension])

    def __str__(self):
        return (self.name)

    
    def get_edit_url(self):
        view_name = "payments:update_bank"
        return reverse(view_name, kwargs={"id": self.pk})



class Payout(models.Model):

    house = models.ForeignKey(House, on_delete=models.CASCADE, blank=False, null=False)
    created_at = models.DateTimeField(default=timezone.now, null=True)
    processed = models.BooleanField(default=False)
    freeze = models.BooleanField(default=False)
    amount = models.DecimalField(blank=True, null=True, max_digits=7, decimal_places=2)
    payout_setting = models.ForeignKey(PayoutSetting, on_delete=models.CASCADE, blank=True, null=True)


    def __str__(self):
        return (self.house.name)



class Transaction(models.Model):
    house = models.ForeignKey(House, on_delete=models.CASCADE, blank=True, null=False)
    created_at = models.DateTimeField(default=timezone.now, null=True)

    amount = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
    house_amount = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
    stripe_amount = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
    arqam_amount = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)

    house_payment = models.BooleanField(default=False)
    payment_id = models.CharField(max_length=150, null=True, blank=True)
    last_four = models.CharField(max_length=10, null=True, blank=True)
    brand = models.CharField(max_length=100, null=True, blank=True)
    network_status = models.CharField(max_length=150, null=True, blank=True)
    risk_level = models.CharField(max_length=150, null=True, blank=True)
    seller_message = models.CharField(max_length=150, null=True, blank=True)
    outcome_type = models.CharField(max_length=150, null=True, blank=True)
    name = models.CharField(max_length=250, null=True, blank=True)
    email = models.EmailField(max_length=300, blank=False, null=False)
    address_line_1 = models.CharField(max_length=150, null=True, blank=True)
    address_state = models.CharField(max_length=150, null=True, blank=True)
    address_postal_code = models.CharField(max_length=150, null=True, blank=True)
    address_city = models.CharField(max_length=150, null=True, blank=True)
    address_country = models.CharField(max_length=150, null=True, blank=True)
    donation_transaction = models.BooleanField(default=False)

    def fee(self):
        fee = self.stripe_amount + self.arqam_amount
        return fee


    def __str__(self):
        return (self.house.name)


class Refund(models.Model):

    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, blank=False, null=False)
    # Amount actually getting refunded
    amount = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
    # Amount to refund from houses account
    house_amount = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
    partial_refund = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now, null=True)

    def __str__(self):
        return (self.transaction.house.name)

    def fee(self):
        fee = self.amount - self.house_amount
        return fee



class HousePayment(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, blank=False, null=False)
    created_at = models.DateTimeField(default=timezone.now, null=True)

    def __str__(self):
        return (self.transaction.house.name)



class ArqamHouseServiceFee(models.Model):
    house = models.ForeignKey(House, on_delete=models.CASCADE, blank=True, null=False)
    created_at = models.DateTimeField(default=timezone.now, null=True)
    amount = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2, default=decimal.Decimal('0.00'))
    live_video = models.BooleanField(default=False)
    free = models.BooleanField(default=False)

    def __str__(self):
        return (self.house.name)


class HouseBalance(models.Model):
    house = models.OneToOneField(House, on_delete=models.CASCADE)
    balance = models.DecimalField(blank=True, null=True, max_digits=8, decimal_places=2)
    gross_balance = models.DecimalField(blank=True, null=True, max_digits=8, decimal_places=2, default=0.00)

    def __str__(self):
        return (self.house.name)


class HouseBalanceLog(models.Model):
    house_balance = models.ForeignKey(HouseBalance, on_delete=models.CASCADE, blank=True, null=True)
    balance = models.DecimalField(blank=True, null=True, max_digits=8, decimal_places=2)
    gross_balance = models.DecimalField(blank=True, null=True, max_digits=8, decimal_places=2, default=0.00)
    opening_balance = models.BooleanField(default=False)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, blank=True, null=True)
    refund = models.ForeignKey(Refund, on_delete=models.CASCADE, blank=True, null=True)
    payout = models.ForeignKey(Payout, on_delete=models.CASCADE, blank=True, null=True)
    house_payment = models.ForeignKey(HousePayment, on_delete=models.CASCADE, blank=True, null=True)
    arqam_house_service_fee = models.ForeignKey(ArqamHouseServiceFee, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now, null=True)

    def __str__(self):
        return (self.house_balance.house.name)





# Update the House Balance and create a house balance log
def house_balance_update(object_type, instance, *args, **kwargs):

    if object_type == 'transaction':
        if not instance.house_payment:
            house_balance = HouseBalance.objects.get(house=instance.house)
            house_balance.balance += instance.house_amount
            house_balance.gross_balance += instance.amount
            house_balance.save()
            house_balance_log = HouseBalanceLog.objects.create(house_balance=house_balance, transaction=instance, balance=house_balance.balance, gross_balance=house_balance.gross_balance)
            house_balance_log.save()

    if object_type == 'refund':
        house_balance = HouseBalance.objects.get(house=instance.transaction.house)
        house_balance.balance -= decimal.Decimal(instance.house_amount)
        house_balance.gross_balance -= decimal.Decimal(instance.amount)
        house_balance.save()
        house_balance_log = HouseBalanceLog.objects.create(house_balance=house_balance, refund=instance, balance=house_balance.balance, gross_balance=house_balance.gross_balance)
        house_balance_log.save()

    if object_type == 'payout':
        house_balance = HouseBalance.objects.get(house=instance.house)
        house_balance.balance -= instance.amount
        # house_balance.gross_balance -= instance.amount
        # Make the gross payment reset to the house balance after a payout
        house_balance.gross_balance = house_balance.balance
        house_balance.save()
        house_balance_log = HouseBalanceLog.objects.create(house_balance=house_balance, payout=instance, balance=house_balance.balance, gross_balance=house_balance.gross_balance)
        house_balance_log.save()
        instance.freeze = True
        instance.save()

    if object_type == 'house_payment':
        house_balance = HouseBalance.objects.get(house=instance.transaction.house)
        house_balance.balance += instance.transaction.house_amount
        house_balance.gross_balance += instance.transaction.amount
        house_balance.save()
        house_balance_log = HouseBalanceLog.objects.create(house_balance=house_balance, house_payment=instance, balance=house_balance.balance, gross_balance=house_balance.gross_balance)
        house_balance_log.save()


    if object_type == 'arqam_house_service_fee':
        if not instance.house.free_live_video:
            house_balance = HouseBalance.objects.get(house=instance.house)
            house_balance.balance -= instance.amount
            house_balance.gross_balance -= instance.amount
            house_balance.save()
            house_balance_log = HouseBalanceLog.objects.create(house_balance=house_balance, arqam_house_service_fee=instance, balance=house_balance.balance, gross_balance=house_balance.gross_balance)
            house_balance_log.save()



# Post Save Methods 
def transaction_post_save_reciever(sender, instance, *args, **kwargs):
    if instance.house_amount:
        house_balance_update(object_type='transaction', instance=instance)

def refund_post_save_reciever(sender, instance, *args, **kwargs):
    house_balance_update(object_type='refund', instance=instance)

def payout_post_save_reciever(sender, instance, *args, **kwargs):
    if not instance.freeze:
        house_balance_update(object_type='payout', instance=instance)

def house_payment_post_save_reciever(sender, instance, *args, **kwargs):
    house_balance_update(object_type='house_payment', instance=instance)


def arqam_house_service_fee_post_save_reciever(sender, instance, *args, **kwargs):
    if instance.amount >= 0.50:
        house_balance_update(object_type='arqam_house_service_fee', instance=instance)

post_save.connect(transaction_post_save_reciever, sender=Transaction)
post_save.connect(refund_post_save_reciever, sender=Refund)
post_save.connect(payout_post_save_reciever, sender=Payout)
post_save.connect(house_payment_post_save_reciever, sender=HousePayment)
post_save.connect(arqam_house_service_fee_post_save_reciever, sender=ArqamHouseServiceFee)




