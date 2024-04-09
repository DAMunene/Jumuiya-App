from django.db import models
from django.contrib.auth.models import User
import secrets
from .paystack import PayStack

#Create your models here
class Customer(models.Model):
    user= models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    name= models.CharField(max_length=200, null=True)
    email=models.CharField(max_length=200)

    def __str__ (self):
        return self.name
    

class Product(models.Model):
    name= models.CharField(max_length=200)
    price=models.FloatField()
    digital=models.BooleanField(default=False, null=True, blank=True)
    image=models.ImageField(null=True, blank=True)

    def __str__ (self):
        return self.name
    
    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url


class Order(models.Model):
    customer=models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    date_ordered=models.DateTimeField(auto_now_add=True)
    complete=models.BooleanField(default=False, null=True, blank=False)
    transaction_id=models.CharField(max_length=100, null=True)

    def __str__(self):
        return f"OrderItem - {self.id}"
    
    @property
    def shipping(self):
        shipping = False
        orderitems = self. orderitem_set.all()
        for i in orderitems:
            if i.product.digital == False:
                shipping = True
        return shipping
    

    
    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])

        return total
    
    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])

        return total
    
    
    
class OrderItem(models.Model):
    product=models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order=models.ForeignKey(Order,on_delete=models.SET_NULL, null=True)
    quantity=models.IntegerField(default=0, null=True, blank=True)
    date_added=models.DateTimeField(auto_now_add=True)

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total
    
    


class ShippingAddress(models.Model):
    customer=models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    order=models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    address=models.CharField(max_length=200, null=False)
    county=models.CharField(max_length=200, null=False)
    town=models.CharField(max_length=200, null=False)
    postalcode=models.CharField(max_length=200, null=False)
    date_added=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Shipping Address {self.address}, {self.town}, {self.county}, {self.postalcode}"

class Payment(models.Model):
    amount=models.PositiveIntegerField()
    ref=models.CharField(max_length=200)
    email=models.EmailField()
    verified=models.BooleanField(default=False)
    date_created=models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-date_created',)

        def __str__(self) -> str:
            return f"Payment: {self.amount}"
        

        
    def save(self, *args, **kwargs) -> None:
        while not self.ref:
            ref= secrets.token_urlsafe(50)
            object_with_similar_ref = Payment.objects.filter(ref=ref)
            if not object_with_similar_ref:
                self.ref = ref
        super().save()


    def amount_value(self) -> int:
        return self.amount *100
    
    def verify_payment(self):
        paystack = PayStack()
        status, result = paystack.verify_payment(self.ref, self.amount)
        if status:
            if result['amount'] / 100 == self.amount:
                self.verified = True
            self.save()
            if self.verified:
                return True
            return False