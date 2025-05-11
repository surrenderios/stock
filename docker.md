在Ubuntu上安装Docker的步骤如下：

### 1. 卸载旧版本（如有）
```bash
sudo apt-get remove docker docker-engine docker.io containerd runc
```

### 2. 安装依赖包
```bash
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg lsb-release
```

### 3. 添加Docker的GPG密钥
```bash
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
```

### 4. 设置Docker仓库
```bash
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

### 5. 安装Docker引擎
```bash
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

### 6. 验证安装
```bash
sudo docker run hello-world
```
成功运行后，会显示Hello from Docker!的欢迎信息。


### 7. 配置镜像加速器
登录阿里云容器镜像服务控制台 https://cr.console.aliyun.com

### 7. 将用户加入docker组（可选，避免每次使用sudo）
```bash
sudo usermod -aG docker $USER
newgrp docker  # 立即生效或重新登录
```

### 注意事项
- **系统兼容性**：确保Ubuntu版本受支持（如20.04 LTS、22.04 LTS）。
- **网络问题**：若下载缓慢，可配置镜像加速器（如阿里云、腾讯云镜像）。
- **权限管理**：加入`docker`组会赋予用户等同于root的权限，需谨慎操作。

### 卸载Docker（如需）
```bash
sudo apt-get purge docker-ce docker-ce-cli containerd.io
sudo rm -rf /var/lib/docker
sudo rm -rf /var/lib/containerd
```

通过上述步骤，即可在Ubuntu系统上顺利完成Docker的安装和基本配置。