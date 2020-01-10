from django.db import models

# Create your models here.
class Orders(models.Model):
    # 微信openid
    openid = models.CharField(max_length=56, blank=True, null=True)
    # 订单号
    order_id = models.CharField(max_length=36, unique=True)
    # 商品标题
    item_title = models.CharField(max_length=70)
    # 商品数量
    item_num = models.IntegerField()
    # 付款时间
    tb_paid_time = models.CharField(max_length=36)
    # 订单号后6位(淘宝id)
    order_id_6 = models.CharField(max_length=12)
    # 预估收入
    pub_share_pre_fee = models.CharField(max_length=10)
    # 结算收入
    total_commission_fee = models.CharField(max_length=10)
    # 订单状态 3：订单结算，12：订单付款， 13：订单失效，14：订单成功
    tk_status = models.IntegerField()


