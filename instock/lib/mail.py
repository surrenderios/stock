#!/usr/bin/env python
# -*- coding: utf-8 -*-

import smtplib
from email.mime.text import MIMEText
from email.header import Header

class QQMailSender:
    def __init__(self, sender_email, auth_code):
        self.smtp_server = "smtp.qq.com"
        self.smtp_port = 587
        self.sender = sender_email
        self.password = auth_code

    def send_mail(self, content, to_user, subject="QMT 运行通知"):
        # 创建邮件内容
        message = MIMEText(content, 'plain', 'utf-8')
        message['From'] = Header(self.sender)
        message['To'] = Header(to_user)
        message['Subject'] = Header(subject)
        
        try:
            # 创建SMTP对象
            smtp_obj = smtplib.SMTP(self.smtp_server, self.smtp_port)
            # 开启TLS加密
            smtp_obj.starttls()
            # 登录邮箱
            smtp_obj.login(self.sender, self.password)
            # 发送邮件
            smtp_obj.sendmail(self.sender, to_user, message.as_string())
            smtp_obj.quit()
            return True, "邮件发送成功"
        except Exception as e:
            return False, f"邮件发送失败: {str(e)}"

# 使用示例
if __name__ == "__main__":
    sender_email = "315828917@qq.com"  # 替换为你的QQ邮箱
    auth_code = "bmvtnrtkibpjbhdi"  # 替换为你的QQ邮箱授权码
    
    mail_sender = QQMailSender(sender_email, auth_code)
    content = "策略开始运行"
    to_user = "surrenderios@gmail.com"  # 替换为接收者的邮箱
    success, message = mail_sender.send_mail(content, to_user)
    print(message)





