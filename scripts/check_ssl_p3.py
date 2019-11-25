import ssl
import socket
from OpenSSL import crypto
import time
import sys

##  此脚本唯一做用为获取ssl证书到期时间
##  此为编写的正常脚本一部分,
##  为了配合公司的python2脚本做出了修改
##  python2 脚本调取运维后台接口,获取被监控域名信息,
##  但是公司的脚本检测报错率太高,所以加入些python3脚本
##  python2主监控脚本以shell方式调用python3脚本,以获取证书信息
##  但是,此主机运行python3脚本时,会报未知的线程错误.
##  所以在python2主监控脚本中,循环15次,每次间隔0.05秒来获取python3脚本中的证书信息
##  一但获取,停止循环,超过次数,以固定格式发送失败信息
##  最后主脚本汇总信息,调用接口,发送telegram信息到运维群和业主群.

def ssl_action(domain):

    context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    sock = socket.socket(socket.AF_INET)
    sock.settimeout(120)
    wrappedSocket = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=domain)
    try:
            ##  模拟游览器访问
        wrappedSocket.connect((domain, 443))
        pem_cert = ssl.DER_cert_to_PEM_cert(wrappedSocket.getpeercert(True))
        wrappedSocket.close()
            ##  获取游览器下载到的证书公钥
        io_cert = crypto.load_certificate(crypto.FILETYPE_PEM, pem_cert)
            ##  获取公钥中的时间
        ssl_time = io_cert.get_notAfter().decode()[:-1]
            ##  格式化时间
        ssl_not_after = ssl_time[0:4] + ' ' + \
                            ssl_time[4:6] + ' ' + \
                            ssl_time[6:8] + ' ' + \
                            ssl_time[8:10] + ' ' + \
                            ssl_time[10:12] + ' ' + \
                            ssl_time[12:14]
        print(True,'+',ssl_not_after)

        #print(True,ssl_not_after)
    except Exception as e:
        # 连接失败，输出错误原因
        print(False,'+',e)

ssl_action(sys.argv[1])

