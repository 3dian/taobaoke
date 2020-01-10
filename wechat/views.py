# coding=utf-8
from decimal import Decimal

from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from . import receive
from . import reply
from . import models
import re
import hashlib
import configparser

# Create your views here.

config = configparser.ConfigParser()
config.read("./config.ini")
token = config['wechat']['token']


# django默认开启了csrf防护，@csrf_exempt是去掉防护
# 微信服务器进行参数交互，主要是和微信服务器进行身份的验证
@csrf_exempt
def check_signature(request):
    if request.method == "GET":
        print("request: ", request)
        # 接受微信服务器get请求发过来的参数
        # 将参数list中排序合成字符串，再用sha1加密得到新的字符串与微信发过来的signature对比，如果相同就返回echostr给服务器，校验通过
        # ISSUES: TypeError: '<' not supported between instances of 'NoneType' and 'str'
        # 解决方法：当获取的参数值为空是传空，而不是传None
        signature = request.GET.get('signature', '')
        timestamp = request.GET.get('timestamp', '')
        nonce = request.GET.get('nonce', '')
        echostr = request.GET.get('echostr', '')
        # 微信公众号处配置的token
        # token = str("Txy159wx")

        hashlist = [token, timestamp, nonce]
        hashlist.sort()
        print("[token, timestamp, nonce]: ", hashlist)

        hashstr = ''.join([s for s in hashlist]).encode('utf-8')
        print('hashstr before sha1: ', hashstr)

        hashstr = hashlib.sha1(hashstr).hexdigest()
        print('hashstr sha1: ', hashstr)

        if hashstr == signature:
            return HttpResponse(echostr)
        else:
            return HttpResponse("weixin index")
    elif request.method == "POST":
        otherContent = autoreply(request)
        return HttpResponse(otherContent)
    else:
        print("你的方法不正确....")


def autoreply(request):
    try:
        webData = request.body
        print("Handle POST webData is: ", webData)

        recMsg = receive.parse_xml(webData)
        if isinstance(recMsg, receive.Msg):
            toUser = recMsg.FromUserName
            fromUser = recMsg.ToUserName
            if recMsg.MsgType == 'text':
                pat_list = ["\₳", "\$", "\¢", "\₴", "\€", "\₤", "\￥", "\＄",
                            "\《"]
                content = recMsg.Content.decode('utf-8')
                for key in pat_list:
                    pat = re.compile(key + r"\w{11}" + key)
                    if len(pat.findall(content)) >= 1:
                        replyMsg = reply.TextMsg(toUser, fromUser, content)
                        tkl_json = replyMsg.tkl_to_json()
                        replyMsg.json_to_Content(tkl_json)
                        return replyMsg.send()
                if "id=" in content:
                    replyMsg = reply.TextMsg(toUser, fromUser, content)
                    link_json = replyMsg.link_to_json()
                    replyMsg.json_to_Content(link_json)
                    return replyMsg.send()
                elif len(content) == 18 and content.isdigit():
                    # 获取openid
                    openid = request.GET['openid']
                    order_res = models.Orders.objects.filter(order_id=content)
                    if len(order_res) > 0:
                        models.Orders.objects.filter(order_id=content).update(
                            openid=openid)
                        item_num = order_res[0].item_num
                        pub_share_pre_fee = float(
                            order_res[0].pub_share_pre_fee) * 0.5
                        pspf = Decimal(str(pub_share_pre_fee)).quantize(
                            Decimal('0.00'))
                        replyMsg = reply.TextMsg(toUser, fromUser, content)
                        replyMsg.order_to_Content(item_num, pspf)
                        return replyMsg.send()
                    else:
                        replyMsg = reply.TextMsg(toUser, fromUser,
                                                 "未查询到该订单,请检查订单号是否有误,或1分钟后重新查询!")
                        return replyMsg.send()
                elif content.lower() == 'h':
                    replyMsg = reply.TextMsg(toUser, fromUser, content)
                    replyMsg.help_msg()
                    return replyMsg.send()
                elif content == '查':
                    pass
                else:
                    replyMsg = reply.TextMsg(toUser, fromUser, "无效输入,请检查后重新输入!")
                    return replyMsg.send()
            if recMsg.MsgType == 'image':
                # Issues1: 'ImageMsg' object has no attribute 'MeidaId'
                # Issues2: 发送图片返回了：qCs1WNDj5p9-FULnsVoNoAIeKQUfLsamrfuXn-Goo32RwoDT8wkhh3QGNjZT0D5a
                # Issues3: 'str' object has no attribute 'decode'
                # Issues4: '该公众号提供的服务出现故障，请稍后再试'
                mediaId = recMsg.MediaId
                replyMsg = reply.ImageMsg(toUser, fromUser, mediaId)
                return replyMsg.send()
            if recMsg.MsgType == 'voice':
                # Issues1: 'ImageMsg' object has no attribute 'MeidaId'
                # Issues2: 发送图片返回了：qCs1WNDj5p9-FULnsVoNoAIeKQUfLsamrfuXn-Goo32RwoDT8wkhh3QGNjZT0D5a
                # Issues3: 'str' object has no attribute 'decode'
                # Issues4: '该公众号提供的服务出现故障，请稍后再试'
                mediaId = recMsg.MediaId
                replyMsg = reply.VoiceMsg(toUser, fromUser, mediaId)
                return replyMsg.send()
            else:
                return reply.Msg().send()
        else:
            print("暂不处理")
            # return "success"
            return reply.Msg().send()
    except Exception as e:
        print(e)


def wechat_js_mpxxx(request):
    return HttpResponse("66hqUSGbYdBXbfKc")
