from aip import AipOcr

import logging
from getconfig import getConfig
if getConfig('output', 'log') == 'True':
    logging.getLogger().setLevel(logging.INFO)
else:
    logging.getLogger().setLevel(logging.ERROR)

APP_ID = '11736241'
API_KEY = 'fUIGmgK2qbKCjqC3SnUdp8Lb'
SECRET_KEY = 'PKqcpphmfITQwLNxbgqkvUYgyjE6BXq2'
client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
use_accurate_ocr = True

def remote_url():
    url = 'http://gcjy.njzwfw.gov.cn/huiyuan/EpointMisTempFile/57312894-66b1-44f0-be66-2d9843b9441b.jpg'
    res = client.webImageUrl(url)
    for item in res['words_result']:
        logging.info(item['words'])
def local_picture_ocr(file_content):
    global use_accurate_ocr
    retry = 3
    while retry != 0:
        try:
            if use_accurate_ocr:
                """ 调用通用文字识别（高精度版） """
                res = client.basicAccurate(file_content)
            else:
                """通用文字识别"""
                res = client.basicGeneral(file_content)
            if 'words_result' in res.keys():
                ocr_result = ''
                for item in res['words_result']:
                    ocr_result += ' '
                    if item['words']:
                        ocr_result += item['words']
                return ocr_result
            else:
                """错误码：17 描述：Open api daily request limit reached"""
                """{'error_msg': 'Open api daily request limit reached', 'error_code': 17}"""
                if 'error_code' in res.keys() and res['error_code'] == 17:
                    use_accurate_ocr = False
                logging.warning('未识别成功, 正在重试...')
                retry -= 1
                continue
        except Exception as e:
            use_accurate_ocr = False
            logging.warning('请求识别文字时出现异常:{0}, 正在重试.'.format(str(e)))
            retry -= 1
    logging.warning('请求文字识别失败!')
    return None


if __name__ == '__main__':
    remote_url()