from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .tasks import *
from django.template import RequestContext
import json

# csrf 例外
# from django.views.decorators.csrf import csrf_exempt
# @csrf_exempt
# Create your views here.

# todo 盘符更新需要思路
# 左导航选项控制[[选项名，是否有次级菜单列表，选项前小图标,选项卡的URL]
Sidebar = [
    ['网盘组状态', [], 'fa fa-dashboard', ''],
    ['网盘列表', [], 'fa fa-edit', 'pans'],
    ['网盘载入', False, 'fa fa-edit', 'addpan'],
    ['数据库设置', False, 'fa fa-circle-o', ''],
    ['Aria2工具', False, 'fa fa-circle-o', ''],
    ['主题设置', False, 'fa fa-circle-o', ''],
]

'''
网盘状态和管理
'''


def panAction(request):
    '''
    网盘状态视图
    :param panName:
    :return:
    '''
    context = {
        'title': '管理-网盘状态',
        'sidebar': sidebar_list('网盘状态', '/manage/'),  # 左导航条
        'pageHeader': '管理-网盘状态',  # 选项卡标题
        'Level': '网盘状态',  # 面包屑次级
        'Here': '',  # 面包屑次级
        'pageHeaderSmall': '未发现挂载网盘',
        'info': '',
    }
    # 如果发现没有挂载网盘json文件，直接跳转网盘添加页
    pansName = returnPanNames()  # 盘符列表
    if not pansName:
        return HttpResponseRedirect("addpan")

    # 检查panName 是否存在和存在于挂载网盘列表中
    if 'name' in request.GET and request.GET['name'] and request.GET['name'] in pansName:  # 获得用户输入值
        context['Here'] = request.GET['name']
        context['pageHeaderSmall'] = request.GET['name']
    else:
        context['Here'] = pansName[0]
        context['pageHeaderSmall'] = pansName[0]

    # 读取 session 的 json 文件
    from .tasks import loadSession
    temp = loadSession('{}.json'.format(context['Here']))
    context['Here'] = temp['panName']

    from odTools.panAction import get_driveInfo
    tempDict = get_driveInfo(temp)
    # print(tempDict)

    # todo 待优化，改成ajax
    # 统计所有图片文件
    from odTools.filesHandler import all_images
    imageRes = all_images(
        temp)  # {'.gif': {'count': 25, 'resSize': {'o': 68987781, 'h': '65M'}}, '.jpg': {'count': 25, 'resSize': {'o': 7000786, 'h': '6M'}}, '.png': {'count': 25, 'resSize': {'o': 28207350, 'h': '26M'}}, '.webp': {'count': 5, 'resSize': {'o': 496770, 'h': '485K'}}, 'Res': {'count': 80, 'resSize': {'o': 104692687, 'h': '99M'}}}    print(imageRes)

    # 统计所有视频文件
    from odTools.filesHandler import all_video
    videoRes = all_video(temp)

    # 统计所有视频文件
    from odTools.filesHandler import all_audio
    audioRes = all_audio(temp)

    # 其他文件统计
    otherFileRes = tempDict['quota']['used'] - imageRes['Res']['resSize']['o'] - videoRes['Res']['resSize']['o'] - \
                   audioRes['Res']['resSize']['o']

    # 格式化字段
    from generalTs.otherHandler import fileSize
    context['info'] = {
        'createdDateTime': tempDict['createdDateTime'].replace('-', '/').replace('T', ' ').replace('Z', ''),
        'lastModifiedDateTime': tempDict['lastModifiedDateTime'].replace('-', '/').replace('T', ' ').replace('Z', ''),
        'name': tempDict['name'],
        'driveType': tempDict['driveType'],
        'owner': tempDict['owner']['user']['displayName'],
        'email': tempDict['owner']['user']['email'],
        'state': tempDict['quota']['state'],
        'deleted': fileSize(tempDict['quota']['deleted']),
        'remaining': dict(fileSize(tempDict['quota']['remaining']), **{
            'percentage': "%.2f%%" % (tempDict['quota']['remaining'] / tempDict['quota']['total'] * 100)}),
        'total': fileSize(tempDict['quota']['total']),
        'used': dict(fileSize(tempDict['quota']['used']),
                     **{'percentage': "%.2f%%" % (tempDict['quota']['used'] / tempDict['quota']['total'] * 100)}),
        'imageRes': dict(imageRes, **{
            'percentage': "%.2f%%" % (imageRes['Res']['resSize']['o'] / tempDict['quota']['total'] * 100)}),
        'videoRes': dict(videoRes, **{
            'percentage': "%.2f%%" % (videoRes['Res']['resSize']['o'] / tempDict['quota']['total'] * 100)}),
        'audioRes': dict(audioRes, **{
            'percentage': "%.2f%%" % (audioRes['Res']['resSize']['o'] / tempDict['quota']['total'] * 100)}),
        'otherFileRes': dict(fileSize(otherFileRes),
                             **{'percentage': "%.2f%%" % (otherFileRes / tempDict['quota']['total'] * 100)}),
    }

    return render(request, 'theme_AdminLTE/management/dashBoard.html', context)


'''
网盘列表相关视图
'''


def pans(request):
    '''
    网盘列表视图
    :param panName:
    :return:
    '''
    # todo 把读取方式改成celery
    context = {
        'title': '管理-网盘列表',
        'sidebar': sidebar_list('网盘列表', '/manage/'),  # 左导航条
        'pageHeader': '管理-网盘列表',  # 选项卡标题
        'Level': '网盘列表',  # 面包屑次级
        'Here': '',  # 面包屑次级
        'pageHeaderSmall': '',
        'files': '',
        'goback': '',
    }
    # 如果发现没有挂载网盘json文件，直接跳转网盘添加页
    pansName = returnPanNames()  # 盘符列表
    if not pansName:
        return HttpResponseRedirect("addpan")

    # 检查panName 是否存在和存在于挂载网盘列表中
    if 'name' in request.GET and request.GET['name'] and request.GET['name'] in pansName:  # 获得用户输入值
        context['Here'] = request.GET['name']
        context['pageHeaderSmall'] = request.GET['name']
    else:
        context['Here'] = pansName[0]
        context['pageHeaderSmall'] = pansName[0]

    # 读取 session 的 json 文件
    from .tasks import loadSession
    temp = loadSession('{}.json'.format(context['Here']))
    context['Here'] = temp['panName']

    # temp = loadSession.delay('/home/rq/workspace/python/AlienVan/driveJsons/anime.json').get()
    from odTools.filesHandler import files_list, reduce_odata
    # 获取需要请求的od路径
    fp = ''
    if 'path' in request.GET and request.GET['path']:
        fp = request.GET['path']
        context['goback'] = '/'.join(request.GET['path'].split('/')[0:-1])  # 返回od上一级路径

    fl = files_list(temp, 1, fp)  # 向od获取odata,文件列表信息需要时间

    context['files'] = [reduce_odata(x) for x in fl['value']]

    return render(request, 'theme_AdminLTE/management/pans.html', context)


def fileShow(request):
    '''
    文件浏览视图
    :return:
    '''
    context = {
        'title': '管理-文件浏览',
        'sidebar': sidebar_list('网盘列表', '/manage/'),  # 左导航条
        'pageHeader': '管理-文件浏览',  # 选项卡标题
        'pageHeaderSmall': '你是在逗我开心对吗？',
        'Level': '网盘列表',  # 面包屑次级
        'Here': '',  # 面包屑次级
        'file': '',
        'urlDict': '',
        'panName': '',
    }
    if 'path' in request.GET and request.GET['path'] and 'name' in request.GET and request.GET['name']:

        # 读取 session 的 json 文件
        from .tasks import loadSession
        temp = loadSession('{}.json'.format(request.GET['name']))
        context['Here'] = temp['panName']
        context['panName'] = temp['panName']
        # 获取对应文件名信息
        from odTools.filesHandler import files_list, reduce_odata
        for i in [reduce_odata(x, 'createdBy') for x in
                  files_list(temp, 1, '/'.join(request.GET['path'].split('/')[0:-1]))['value']]:
            if i['name'] == request.GET['path'].split('/')[-1]:
                context['file'] = i
                # 通过文件类型构造各类引用链接
                if 'image' in i['mimeType']:
                    context['urlDict'] = {
                        '图片 分享': i['thumbnails'][0]['large']['url'],
                        'html 引用': '<img src="{}">'.format(i['thumbnails'][0]['large']['url']),
                        'Markdown 引用': '![{name}]({url})'.format(name=i['name'],
                                                                 url=i['thumbnails'][0]['large']['url']),
                    }
                elif 'text' in i['mimeType']:

                    context['urlDict'] = {
                        '文本 分享': i['download'],
                        'html 引用': i['download'],
                    }

                break

    return render(request, 'theme_AdminLTE/management/itemInfo.html', context)


def fileDel(request):
    '''
    文件删除
    :return:
    '''
    # 如果发现没有挂载网盘json文件，直接跳转网盘添加页
    pansName = returnPanNames()  # 盘符列表
    if not pansName:
        return HttpResponseRedirect("addpan")

    # 如果无文件id和动作参数，则跳转到对应盘根目录
    if 'fileid' in request.GET and request.GET['fileid'] and 'name' in request.GET and request.GET['name']:

        # 读取 session 的 json 文件
        from .tasks import loadSession
        client = loadSession('{}.json'.format(request.GET.get('name')))

        # 删除对应文件
        # todo 有待改成post
        from odTools.filesHandler import delete_files
        nya = delete_files(client, request.GET['fileid'])

        return HttpResponseRedirect("pans?name={}".format(request.GET.get('name')))
    else:
        return HttpResponseRedirect("pans?name={}".format(request.GET.get('name', pansName[0])))


def fileRename(request):
    '''
    文件重命名
    :return:
    '''
    pansName = returnPanNames()  # 盘符列表
    # 如果无文件id和动作参数，则跳转到对对应盘根目录
    if 'fileid' in request.POST and request.POST['fileid'] \
            and 'fileName' in request.POST and request.POST['fileName'] \
            and 'panName' in request.POST and request.POST['panName'] and request.POST['panName'] in pansName:

        # 读取 session 的 json 文件
        from .tasks import loadSession
        client = loadSession('{}.json'.format(request.POST.get('panName')))

        # # 给对应文件改名
        from odTools.filesHandler import rename_files
        rename_res = rename_files(client, request.POST['fileid'], request.POST['fileName'])

        # 响应请求，回复信息
        # todo 返回消息跳转到新文件页
        if '@microsoft.graph.downloadUrl' in rename_res.keys():
            return JsonResponse({'status': 'success', 'info': ''})
        else:
            return JsonResponse({'status': 'Fuck', 'info': ''})
    else:
        # 缺少必须的字段全部500
        return HttpResponse(status=500)


def addPan(request):
    '''
    添加网盘视图
    :return:
    '''
    from odTools.authHandler import get_sign_in_url
    sign_in_url, state = get_sign_in_url()
    context = {
        'title': '管理-网盘载入',
        'sidebar': sidebar_list('网盘载入', '/manage/'),  # 左导航条
        'pageHeader': '网盘载入',  # 选项卡标题
        'Level': '网盘载入',  # 面包屑次级
        'Here': '网盘载入',  # 面包屑次级
        'pageHeaderSmall': '没有载入网盘，就什么也做不了..emmmmm',
        'authUrl': sign_in_url,
        'info': '',
    }
    if 'code' in request.GET and request.GET['code']:  # 获得用户输入值
        driveInfo = {
            'panName': request.GET.get('panName'),
            'code': request.GET.get('code'),
            'odtype': request.GET.get('odtype'),
        }
        for i in driveInfo:
            if not driveInfo[i]:
                context['info'] = '信息不完整，要填完哦'

                return render(request, 'theme_AdminLTE/management/loadDrive.html', context)

        from .tasks import getAuth
        client = getAuth.delay(driveInfo).get()
        print(client)
        # context['info'] = '添加成功～'+client
        context['info'] = client

    return render(request, 'theme_AdminLTE/management/loadDrive.html', context)


def fileupLoader(request):
    '''
    上传文件
    :return:
    '''
    # 如果发现没有挂载网盘json文件，直接跳转网盘添加页
    pansName = returnPanNames()  # 盘符列表

    from alienVan.settings import MEDIA_ROOT
    filesdata = request.FILES.get('filesdata', None)
    panName = request.POST.get('panname', None)
    panPath = request.POST.get('path', None)
    if filesdata and panName and panName in pansName:

        # 保存文件到硬盘中
        file_dir = os.path.join(MEDIA_ROOT, filesdata.name)
        print(file_dir)
        with open(file_dir, "wb") as f:
            for chunk in filesdata.chunks():
                f.write(chunk)

        # 读取 session 的 json 文件
        from .tasks import loadSession
        client = loadSession('{}.json'.format(panName))

        # 上传文件到对应网盘
        from odTools.uploader import main_uploader
        file_res = main_uploader(client, file_dir, panPath)
        print(file_res)

        # 验证是否成功上传到OD
        if 'status' in file_res.keys() and file_res['status'] == 'ok':
            # 成功则删除缓存
            if os.path.exists(file_dir):
                # 删除文件，可使用以下两种方法。
                os.remove(file_dir)
                # os.unlink(my_file)

            return JsonResponse({'status': 'success'})
        else:
            return HttpResponse(status=400)
    else:
        return HttpResponse(status=400)


# 视图辅助函数


def sidebar_list(active, appURL=None):
    '''
    ⎛⎝≥⏝⏝≤⎠⎞
    :param active:
    :param appURL:
    :return:
    '''
    pansName = returnPanNames()  # 盘符列表

    getValue = '#'  # 左导航下拉菜单超链接
    if appURL:
        getValue = '?name='

    htmlDict = {
        'li': '<li class="{active}"><a href="{url}"><i class="{i}"></i> <span>{name}</span></a></li>',
        'menuLi': '<li><a href="{url}">{text}</a></li>',
        'treeview': '<li class="treeview active"><a href="#"><i class="{i}"></i> <span>{name}</span><span class="pull-right-container"><i class="fa fa-angle-left pull-right"></i></span></a><ul class="treeview-menu">{li}</ul></li>',
    }

    temp = []
    for i in Sidebar:
        menuLi = i[1]
        if i[1] == []:
            menuLi = pansName

        if i[0] == active:
            if menuLi:
                tempStr = htmlDict['treeview'].format(active='active', i=i[2], name=i[0], li=''.join(
                    [htmlDict['menuLi'].format(url=appURL + i[3] + getValue + x, text=x) for x in menuLi]))
            else:
                tempStr = htmlDict['li'].format(active='active', url=i[3], i=i[2], name=i[0])
        else:
            if menuLi:
                tempStr = htmlDict['treeview'].format(active='', i=i[2], name=i[0], li=''.join(
                    [htmlDict['menuLi'].format(url=appURL + i[3] + getValue + x, text=x) for x in menuLi]))
            else:
                tempStr = htmlDict['li'].format(active='', url=i[3], i=i[2], name=i[0])

        temp.append(tempStr)

    return ''.join(temp)


if __name__ == '__main__':
    # from management.tasks import test
    # a = test.delay(1,2).get()
    # print(Sidebar)
    pass
