import threading

from django.shortcuts import render, redirect
from django.http import *
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from AiDream.settings import DEBUG
from AiDream.models import embeddingInfo, generateInfo
from django.utils.translation import gettext as _
from captcha.models import CaptchaStore
from captcha.helpers import  captcha_image_url

# 创建验证码
def captcha():
    hashkey = CaptchaStore.generate_key()   #验证码答案
    image_url = captcha_image_url(hashkey)  #验证码地址
    captcha = {'hashkey': hashkey, 'image_url': image_url}
    return captcha

# 刷新验证码
def refresh_captcha(request):
    return JsonResponse(captcha())

# 验证验证码
def jarge_captcha(captchaStr, captchaHashkey):
    if captchaStr and captchaHashkey:
        try:
            # 获取根据hashkey获取数据库中的response值
            get_captcha = CaptchaStore.objects.get(hashkey=captchaHashkey)
            if get_captcha.response == captchaStr.lower():     # 如果验证码匹配
                return True
        except:
            return False
    else:
        return False

from pyDes import des, PAD_PKCS5, CBC
import zlib, zipfile, os
import json, time, re, base64, hashlib, urllib
import uuid, requests
import shutil
import cv2

import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

import openai
openai.api_key = "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"


PATH = '.'
MODEL_PATH = r"G:\novelai-webui-aki-v2_web"
DJANGO_SERVER_URL = "http://9yw8spn.nat.ipyingshe.com"  # 用于发送邮件
MODEL_SERVER_URL = "http://127.0.0.1:7860"


tipTemplateFilePath = rf"{MODEL_PATH}\textual_inversion_templates\subject_filewords.txt"
# try:
#     for i in json.loads(re.search(r"<script>window.gradio_config = ({.*});</script>", requests.get(f"{MODEL_SERVER_URL}/").text).group(1))['components']:
#         if i['id'] == 532:
#             tipTemplateFilePath = i['props']['value']
# except:
#     pass

def safeMkdir(path):
    if not os.path.exists(path):
        os.mkdir(path)


def ResziePadding(src, dst, fixed_side=128):
    img = cv2.imread(src)
    h, w = img.shape[0], img.shape[1]
    scale = max(w, h) / float(fixed_side)  # 获取缩放比例
    new_w, new_h = int(w / scale), int(h / scale)
    resize_img = cv2.resize(img, (new_w, new_h))  # 按比例缩放

    # 计算需要填充的像素长度
    if new_w % 2 != 0 and new_h % 2 == 0:
        top, bottom, left, right = (fixed_side - new_h) // 2, (fixed_side - new_h) // 2, (fixed_side - new_w) // 2 + 1, (
                fixed_side - new_w) // 2
    elif new_w % 2 == 0 and new_h % 2 != 0:
        top, bottom, left, right = (fixed_side - new_h) // 2 + 1, (fixed_side - new_h) // 2, (fixed_side - new_w) // 2, (
                fixed_side - new_w) // 2
    elif new_w % 2 == 0 and new_h % 2 == 0:
        top, bottom, left, right = (fixed_side - new_h) // 2, (fixed_side - new_h) // 2, (fixed_side - new_w) // 2, (
                fixed_side - new_w) // 2
    else:
        top, bottom, left, right = (fixed_side - new_h) // 2 + 1, (fixed_side - new_h) // 2, (fixed_side - new_w) // 2 + 1, (
                fixed_side - new_w) // 2

    # 填充图像
    pad_img = cv2.copyMakeBorder(resize_img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=[0, 0, 0])

    cv2.imwrite(dst, pad_img)


def dotaskList(taskList):
    for i in taskList:
        if 'generate_id' in i:
            generate_keyword = i['generate_keyword']
            generate_opposite_keyword = i['generate_opposite_keyword']
            embeddingList = list(embeddingInfo.objects.filter(embedding_creator=i['generate_creator'], embedding_status=True).values())
            for embedding in embeddingList:
                for k in range(len(generate_keyword)):
                    if generate_keyword[k] == embedding['embedding_name']:
                        generate_keyword[k] = embedding['embedding_id']
                for k in range(len(generate_opposite_keyword)):
                    if generate_opposite_keyword[k] == embedding['embedding_name']:
                        generate_opposite_keyword[k] = embedding['embedding_id']

            print("开始生图任务 id:", i['generate_id'], generate_keyword, generate_opposite_keyword)

            req_data = {
                "fn_index": 102,
                "data": [
                    ", ".join(generate_keyword),  # 提示词
                    ", ".join(generate_opposite_keyword),  # 反向提示词
                    "None",  # 模版风格 1
                    "None",  # 模版风格 2
                    28,  # 采样迭代步数(Steps)
                    "Euler a",  # 采样方法(Sampler)
                    i['generate_face_fix'],  # 面部修复
                    False,  # 可平铺(Tiling)
                    i['generate_round'],  # 生成批次
                    i['generate_num'],  # 每批数量
                    7,  # 提示词相关性(CFG Scale)
                    i['generate_seed'],  # 随机种子(seed)
                    -1,  # 差异随机种子
                    0,  # 差异强度
                    0,  # 宽度(Resize seed)
                    0,  # 高度(Resize seed)
                    False,
                    i['generate_width'],  # 宽度
                    i['generate_height'],  # 高度
                    False,  # 高分辨率修复
                    0.7,
                    0,
                    0,
                    "None",
                    i['generate_art_width'] / 100,  # 美术风格权重
                    i['generate_art_step'],  # 美术风格迭代步数
                    "0.0001",  # 美术风格学习率
                    False,  # 球面线性插值
                    "None",  # 美术风格图集 embedding
                    "",  # 该图集的美术风格描述
                    0.1,  # 球面线性插值角度
                    False,
                    False,
                    False,
                    False,
                    "",
                    "Seed",
                    "",
                    "Nothing",
                    "",
                    True,
                    False,
                    False,
                    None,
                    "",
                    ""
                ]
            }
            rsp_data = requests.post(f"{MODEL_SERVER_URL}/run/predict/", data=json.dumps(req_data, ensure_ascii=False, separators=(',', ':')).encode('utf-8')).json()
            safeMkdir(f"{PATH}/data/generate/{i['generate_id']}/")
            num = 0
            for k in rsp_data['data'][0]:
                shutil.copyfile(k['name'], f"{PATH}/data/generate/{i['generate_id']}/{str(num).rjust(2, '0')}.png")
                num += 1
            generate_obj = generateInfo.objects.get(generate_id=i['generate_id'])
            generate_obj.generate_status = True
            generate_obj.save()

            # 发送提醒邮件
            mail_msg = '<p>'+_("AI图生图")+" "+_("生图任务完成")+f'</p><p><a href="{DJANGO_SERVER_URL}/home">'+_("点击前往查看")+'</a></p>'
            sendEmail(i['generate_creator'], mail_msg, _("AI图生图")+" "+_("生图任务完成"))
        elif 'embedding_id' in i:
            print("开始创建Tag任务 id:", i['embedding_id'])

            # 创建 Embedding
            req_data = {
                "fn_index": 145,
                "data": [
                    i['embedding_id'],  # 名称
                    "*",  # 初始化文字
                    2,  # 每个词元(token)的向量数
                    False  # 覆写旧的 Embedding
                ]
            }
            rsp_data = requests.post(f"{MODEL_SERVER_URL}/run/predict/", data=json.dumps(req_data, ensure_ascii=False, separators=(',', ':'))).json()
            print("创建 Embedding", rsp_data)

            for trainInfo in [[256, 4, 0.02, 2000], [384, 2, 0.01, 4000], [512, 1, 0.005, 6000]]:
                size = trainInfo[0]
                safeMkdir(f"{PATH}/data/embedding/{i['embedding_id']}/{size}")
                safeMkdir(f"{PATH}/data/embedding/{i['embedding_id']}/{size}/src")
                safeMkdir(f"{PATH}/data/embedding/{i['embedding_id']}/{size}/dst")
                for file in os.listdir(f"{PATH}/data/embedding/{i['embedding_id']}/upload/"):
                    ResziePadding(f"{PATH}/data/embedding/{i['embedding_id']}/upload/{file}", f"{PATH}/data/embedding/{i['embedding_id']}/{size}/src/{file}", size)

                # 原生预处理
                req_data = {
                    "fn_index": 147,
                    "data": [
                        rf"AiDream4\data\embedding\{i['embedding_id']}\{size}\src",  # 源目录
                        rf"AiDream4\data\embedding\{i['embedding_id']}\{size}\dst",  # 目标目录
                        size,  # 宽度
                        size,  # 高度
                        "ignore",  # 对已有的 txt 描述文本的行为
                        True,  # 创建镜像副本
                        False,  # 分割过大的图像
                        True,  # 使用 BLIP 生成说明文字(自然语言描述)
                        True,  # 使用 deepbooru 生成说明文字(tags)
                        0.5,  # 图像分割阈值
                        0.2,  # 分割图像重叠的比率
                        False,  # 自动焦点裁切
                        0.9,  # 焦点面部权重
                        0.15,  # 焦点熵权重
                        0.5,  # 焦点线条权重
                        False,  # 创建调试(debug)图片
                        "",
                        ""
                    ]
                }
                rsp_data = requests.post(f"{MODEL_SERVER_URL}/run/predict/", data=json.dumps(req_data, ensure_ascii=False, separators=(',', ':'))).json()
                print("预处理", size, rsp_data)

                # 训练
                req_data = {
                    "fn_index": 148,
                    "data": [
                        i['embedding_id'],  # Embedding
                        str(trainInfo[2]),  # Embedding 学习率
                        trainInfo[1],  # 每批数量
                        rf"AiDream4\data\embedding\{i['embedding_id']}\{size}\dst",  # 数据集目录
                        "textual_inversion",  # 日志目录
                        size,  # 宽度
                        size,  # 高度
                        trainInfo[3],  # 最大迭代步数
                        500,  # 每 N 步保存一个图像到日志目录，0 表示禁用
                        500,  # 每 N 步将 embedding 的副本保存到日志目录，0 表示禁用
                        tipTemplateFilePath,  # 提示词模版文件
                        True,  # 保存图像，并在 PNG 图片文件中嵌入 embedding 文件
                        False,  # 进行预览时，从文生图选项卡中读取参数（提示词等）
                        "",
                        "",
                        28,
                        "Euler a",
                        7,
                        -1,
                        512,
                        512,
                        "",
                        ""
                    ]
                }
                rsp_data = requests.post(f"{MODEL_SERVER_URL}/run/predict/", data=json.dumps(req_data, ensure_ascii=False, separators=(',', ':')).encode('utf-8')).json()
                print("训练", size, rsp_data)

            embeddingInfo_obj = embeddingInfo.objects.get(embedding_id=i['embedding_id'])
            embeddingInfo_obj.embedding_status = True
            embeddingInfo_obj.save()
            try:
                shutil.rmtree(f"{PATH}/data/embedding/{i['embedding_id']}/")
            except:
               pass

            # 发送提醒邮件
            mail_msg = '<p>'+_("AI图生图")+" "+_("Tag创建任务完成")+f'</p><p><a href="{DJANGO_SERVER_URL}/home">'+_("点击前往查看")+'</a></p>'
            sendEmail(i['embedding_creator'], mail_msg, _("AI图生图")+" "+_("Tag创建任务完成"))
        break


def taskListManage():  # 用于任务队列协调
    while True:
        taskList = list(embeddingInfo.objects.filter(embedding_status=False).values()) + list(generateInfo.objects.filter(generate_status=False).values())
        taskList = sorted(taskList, key=lambda x: (x['embedding_time'] if 'embedding_time' in x else x['generate_time']))
        try:
            dotaskList(taskList)
        except:
            if DEBUG:
                raise
            pass
        time.sleep(5)


thread = threading.Thread(target=taskListManage)


thread.start()


def generateUUID():
    return str(uuid.uuid4()).replace("-", "")


def des_encode(input_var, mode='str', iszip=True):
    content = input_var.encode() if mode == 'str' else input_var if mode == 'bytes' else input_var
    if iszip:
        content = zlib.compress(content)
    secret_key = 'DrTeamst'
    iv = secret_key
    k = des(secret_key, CBC, iv, pad=None, padmode=PAD_PKCS5)
    en = k.encrypt(content, padmode=PAD_PKCS5)
    return base64.b64encode(en).decode()


def des_decode(input_var, mode='str', iszip=True):
    secret_key = 'DrTeamst'
    iv = secret_key
    k = des(secret_key, CBC, iv, pad=None, padmode=PAD_PKCS5)
    de = k.decrypt(base64.b64decode(input_var), padmode=PAD_PKCS5)
    if iszip:
        de = zlib.decompress(de)
    return de.decode() if mode == 'str' else de if mode == 'bytes' else de


def md5_encode(enstr):  # 计算md5
    return hashlib.md5(enstr.encode()).hexdigest()


def sendEmail(receiver, mail_msg, title):
    message = MIMEText(mail_msg, 'html', 'utf-8')
    message['From'] = formataddr([_("AI图生图"), "2587297563@qq.com"])
    message['To'] = formataddr([receiver, receiver])
    message['Subject'] = title
    try:
        server = smtplib.SMTP_SSL("smtp.qq.com", 465)
        server.login("2587297563@qq.com", "icdtmcsaarfyebdb")
        server.sendmail('2587297563@qq.com', [receiver, ], message.as_string())
        server.quit()
        return True
    except:
        if DEBUG:
            raise
        return False


def register(request):  # 注册
    if request.user.is_authenticated:
        return redirect("/home")
    if request.method == "GET":
        return render(request, "register.html", {"captcha": captcha()})
    if request.method == "POST":
        if not jarge_captcha(request.POST.get("captcha"),request.POST.get("hashkey")):
            return render(request, "info.html", {"title": _("注册失败"), "info": _("验证码错误"), "returnUrl": "/register"})
        email = request.POST.get("email")
        password = request.POST.get("password")
        if len(email) > 50:
            return render(request, "info.html", {"title": _("注册失败"), "info": _("邮箱长度不能超过50字符"), "returnUrl": "/register"})
        if len(password) > 30 or len(password) < 8 or (not email) or (not password):
            return render(request, "info.html", {"title": _("注册失败"), "info": _("请检查表单填写状况"), "returnUrl": "/register"})

        if User.objects.filter(username=email):
            return render(request, "info.html", {"title": _("注册失败"), "info": _("用户已注册"), "returnUrl": "/login"})

        confirmUrl = DJANGO_SERVER_URL + "/registerConfirm?info=" + urllib.parse.quote(des_encode(json.dumps({"email": email, "password": password, "time": int(time.time())}, ensure_ascii=False)))
        mail_msg = '<p>'+_("AI图生图")+" "+_("注册确认邮件")+f'</p><p><a href="{confirmUrl}">'+_("请点击此处确认注册")+'</a></p>'
        
        # if DEBUG:
        #     time.sleep(2)
        #     return HttpResponse(mail_msg)

        if sendEmail(email, mail_msg, _("AI图生图")+" "+_("注册确认邮件")):
            return render(request, "info.html", {"title": _("注册确认邮件发送成功"), "info": _("请在30分钟内前往邮箱确认注册")})
        else:
            return render(request, "info.html", {"title": _("注册失败"), "info": _("邮件发送失败"), "returnUrl": "/register"})


def registerConfirm(request):  # 注册确认
    registerInfo = json.loads(des_decode(request.GET.get("info")))
    if User.objects.filter(username=registerInfo['email']):
        return render(request, "info.html", {"title": _("注册失败"), "info": _("用户已注册"), "returnUrl": "/login"})
    if (time.time() - registerInfo['time']) > 30 * 60:
        return render(request, "info.html", {"title": _("注册失败"), "info": _("有效期已过"), "returnUrl": "/login"})
    User.objects.create_user(username=registerInfo['email'], password=registerInfo['password']).save()
    return render(request, "info.html", {"title": _("注册成功"), "info": _("请前往登录"), "returnUrl": "/login"})


def login(request):  # 登录
    if request.user.is_authenticated:
        return redirect("/home")
    if request.method == "GET":
        return render(request, "login.html", {"captcha": captcha()})
    if request.method == "POST":
        if not jarge_captcha(request.POST.get("captcha"),request.POST.get("hashkey")):
            return render(request, "info.html", {"title": _("登录失败"), "info": _("验证码错误"), "returnUrl": "/login"})
        email = request.POST.get("email")
        password = request.POST.get("password")
        if (not email) or (not password):
            return render(request, "info.html", {"title": _("登录失败"), "info": _("请检查表单填写状况"), "returnUrl": "/login"})
        user_obj = auth.authenticate(username=email, password=password)
        if not user_obj:
            return render(request, "info.html", {"title": _("登录失败"), "info": _("用户名或密码输入错误"), "returnUrl": "/login"})
        auth.login(request, user_obj)
        return redirect("/home")


@login_required(login_url='/login')
def resetPassword(request):  # 注册
    if request.method == "GET":
        return render(request, "resetPassword.html")
    if request.method == "POST":
        oldPassword = request.POST.get("oldPassword")
        newPassword = request.POST.get("newPassword")
        if (not oldPassword) or (not newPassword):
            return render(request, "info.html", {"title": _("修改失败"), "info": _("请检查表单填写状况"), "returnUrl": "/resetPassword"})

        user_obj = auth.authenticate(username=request.user.username, password=oldPassword)
        if not user_obj:
            return render(request, "info.html", {"title": _("修改失败"), "info": _("旧密码输入错误"), "returnUrl": "/resetPassword"})
        user_obj.set_password(newPassword)
        user_obj.save()
        auth.logout(request)
        return render(request, "info.html", {"title": _("修改成功"), "info": _("请重新登录"), "returnUrl": "/login"})


@login_required(login_url='/login')
def logout(request):
    auth.logout(request)
    return redirect("/login")


@login_required(login_url='/login')
def home(request):
    embeddingList = list(embeddingInfo.objects.filter(embedding_creator=request.user.username).values())
    for i in embeddingList:
        i['embedding_time'] = i['embedding_time'].strftime("%Y-%m-%d %H:%M:%S")
        del i['embedding_creator']
        del i['id']

    generateList = list(generateInfo.objects.filter(generate_creator=request.user.username).values())
    for i in generateList:
        i['generate_time'] = i['generate_time'].strftime("%Y-%m-%d %H:%M:%S")
        i['generate_keyword'] = ", ".join(i['generate_keyword'])
        i['generate_opposite_keyword'] = ", ".join(i['generate_opposite_keyword'])
        del i['generate_creator']
        del i['id']
    return render(request, 'home.html', {'path': 'home', 'embeddingList': json.dumps(embeddingList[::-1], ensure_ascii=False), "generateList": json.dumps(generateList[::-1], ensure_ascii=False)})


@login_required(login_url='/login')
def addGenerateTask(request):
    if request.method == 'POST':
        if not request.POST.get("keyword", ""):
            return render(request, "info.html", {"title": _("添加任务失败"), "info": _("请检查表单填写状况"), "returnUrl": "/home"})
        generate_keyword = [i.strip() for i in request.POST.get("keyword").split(",")]
        generate_opposite_keyword = [i.strip() for i in request.POST.get("opposite_keyword").split(",")]

        generate_width = int(request.POST.get("width"))
        generate_height = int(request.POST.get("height"))
        generate_round = int(request.POST.get("round"))
        generate_num = int(request.POST.get("num"))
        generate_art_width = int(request.POST.get("art_width"))
        generate_art_step = int(request.POST.get("art_step"))
        generate_face_fix = (request.POST.get("face_fix") == "on")
        generate_seed = int(request.POST.get("seed"))

        generateInfo.objects.create(
            generate_id=generateUUID(),
            generate_keyword=generate_keyword,
            generate_opposite_keyword=generate_opposite_keyword,
            generate_width=generate_width,
            generate_height=generate_height,
            generate_round=generate_round,
            generate_num=generate_num,
            generate_art_width=generate_art_width,
            generate_art_step=generate_art_step,
            generate_face_fix=generate_face_fix,
            generate_seed=generate_seed,
            generate_creator=request.user.username
        )
        return render(request, "info.html", {"title": _("任务创建成功"), "info": _("请去往生图管理下载图片"), "returnUrl": "/home"})


@login_required(login_url='/login')
def addEmbeddingTask(request):
    if request.method == 'POST':
        if not request.POST.get("name", ""):
            return render(request, "info.html", {"title": _("添加任务失败"), "info": _("请检查表单填写状况"), "returnUrl": "/home"})
        embedding_name = request.POST.get("name").strip()
        embeddingList = list(embeddingInfo.objects.filter(embedding_creator=request.user.username).values())
        for i in embeddingList:
            if i['embedding_name'] == embedding_name:
                return render(request, "info.html", {"title": _("添加任务失败"), "info": _("Tag名称已存在"), "returnUrl": "/home"})
        embedding_files = request.POST.get("file_upload").split('_')
        if len(embedding_files) == 0:
            return render(request, "info.html", {"title": _("添加任务失败"), "info": _("无照片"), "returnUrl": "/home"})
        embedding_id = generateUUID()

        safeMkdir(f"{PATH}/data/embedding/{embedding_id}/")
        safeMkdir(f"{PATH}/data/embedding/{embedding_id}/upload/")

        num = 0
        for i in embedding_files:
            os.rename(f"{PATH}/data/upload_image/{i}.png", f"{PATH}/data/embedding/{embedding_id}/upload/{str(num).rjust(2, '0')}.png")
            num += 1

        embeddingInfo.objects.create(
            embedding_id=embedding_id,
            embedding_name=embedding_name,
            embedding_creator=request.user.username
        )
        return render(request, "info.html", {"title": _("任务创建成功"), "info": _("请等待任务完成"), "returnUrl": "/home"})


@login_required(login_url='/login')
def uploadImage(request):
    file_obj = request.FILES.get('file')
    file_uuid = generateUUID()
    with open(f"{PATH}/data/upload_image/{file_uuid}.png", 'wb') as f:
        for i in file_obj.chunks():
            f.write(i)
    return JsonResponse({"code": 0, "msg": "", "fileid": file_uuid})


@login_required(login_url='/login')
def showGenerateImage(request):
    generate_id = request.GET.get("id")

    file_list = os.listdir(f'{PATH}/data/generate/{generate_id}/')

    return render(request, "showImage.html", {"generate_id": generate_id, "file_list": file_list})


@login_required(login_url='/login')
def getGenerateImage(request):
    generate_id = request.GET.get("id")
    file_name = request.GET.get("name")
    response = FileResponse(open(f'{PATH}/data/generate/{generate_id}/{file_name}', 'rb'))
    response['content_type'] = "application/image"
    return response


@login_required(login_url='/login')
def downloadGenerateImage(request):
    generate_id = request.GET.get("id")
    if not os.path.exists(f"{PATH}/data/generate/{generate_id}.zip"):
        z = zipfile.ZipFile(f"{PATH}/data/generate/{generate_id}.zip", "w")
        for i in os.listdir(f'{PATH}/data/generate/{generate_id}/'):
            z.write(f'{PATH}/data/generate/{generate_id}/{i}', f"{i}")
        z.close()

    response = FileResponse(open(f"{PATH}/data/generate/{generate_id}.zip", 'rb'))
    response['content_type'] = "application/octet-stream"
    fileName = urllib.parse.quote(f"{generate_id}.zip")
    response['Content-Disposition'] = f'attachment; filename="{fileName}"'
    return response

@login_required(login_url='/login')
def chatgptTagGenerate(request):
    describe = request.body
    if not describe:
        return HttpResponse('')
    #prompt = _("为NovelAI写一段描写如下要素的tag：")+f"({describe}). "+_("输出格式：要素1，要素2，要素3……")+_("以此类推，用英文，至少45个要素，不重复并为比较重要的要素加上括号")
    prompt = ('''以下提示用于指导Al绘画模型创建图像。它们包括人物外观、背景、颜色和光影效果，以及图像的主题和风格等各种细节。
这些提示的格式通常包括带权重的数字括号，用于指定某些细节的重要性或强调。例如，"(masterpiece:1.4)"表示作品的质量非常重要。
以下是一些示例：
1. (8k, RAW photo, best quality, masterpiece:1.2),(realistic, photo-realistic:1.37), ultra-detailed, 1girl, cute, solo, beautiful detailed sky, detailed cafe, night, sitting, dating, (nose blush), (smile:1.1),(closed mouth), medium breasts, beautiful detailed eyes, (collared shirt:1.1), bowtie, pleated skirt, (short hair:1.2), floating hair, ((masterpiece)), ((best quality)),
2. (masterpiece, finely detailed beautiful eyes: 1.2), ultra-detailed, illustration, 1 girl, blue hair black hair, japanese clothes, cherry blossoms, tori, street full of cherry blossoms, detailed background, realistic, volumetric light, sunbeam, light rays, sky, cloud,
3. highres, highest quallity, illustration, cinematic light, ultra detailed, detailed face, (detailed eyes, best quality, hyper detailed, masterpiece, (detailed face), blue hairlwhite hair, purple eyes, highest details, luminous eyes, medium breats, black halo, white clothes, backlighting, (midriff:1.4), light rays, (high contrast), (colorful)

仿照之前的提示，写一段描写如下要素的提示：
''' + str(describe))
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=2048
    )
    if response["choices"][0]["text"][-1] == '.':
        response["choices"][0]["text"] = response["choices"][0]["text"][0:-1]
    return JsonResponse({"code": 0, "msg": response["choices"][0]["text"].strip()})

@login_required(login_url='/login')
def delEmbedding(request):
    embedding_id = request.body.decode()
    embeddingInfo.objects.get(embedding_id = embedding_id).delete()
    try:
        shutil.rmtree(f"{PATH}/data/embedding/{embedding_id}/")
    except:
        pass
    os.remove(rf"{MODEL_PATH}\embeddings\{embedding_id}.pt")
    return JsonResponse({"code": 0, "msg": ""})



def layui_icon(request):
    return redirect('/static/image/icon.png')
