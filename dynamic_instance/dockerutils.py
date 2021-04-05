import docker
from CTFd.models import Challenges, db
from .models import *
import random
import os 
import socket

#获取随机端口
def randomport(port,ip):
    if port == 80:
        out_port=random.randint(8000,8999)
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            s.connect((ip,int(out_port)))
            s.shutdown(2)
            randomport(port,ip)
        except Exception as e:
            return out_port
    else:
        out_port=random.randint(20000,30000)
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            s.connect((ip,int(out_port)))
            s.shutdown(2)
            randomport(port,ip)
        except Exception as e:
            return out_port
#创建 延长 重载 销毁实例
class Instance:
    
    @classmethod
    def bootinstance(cls,imagename,instanceid):
        print("booting instance")
        result=""
        
        instance=Instances.query.filter_by(id=instanceid).first()
        try:
            image=ChallengeImages.query.filter_by(name=imagename).first()
            server=Servers.query.filter_by(tag=image.pullimage).first()
        except Exception as e:
            db.session.delete(instance)
            db.session.commit()
            return json.dumps("fail: {}".format(e))
        #开始加载docker容器 分两种情况,本地服务器与远程服务器
        if server.tag=="local":
            try:
                client=docker.from_env()
            except Exception as e:
                db.session.delete(instance)
                db.session.commit()
        
                return json.dumps("fail: {}".format(e))
        else:
            tls_config = docker.tls.TLSConfig(client_cert=(server.client_cert_file, server.client_key_file))
            try:
                client=docker.DockerClient(base_url=server.socket,tls=tls_config)
            except Exception as e:
                db.session.delete(instance)
                db.session.commit()
                return json.dumps("fail: {}".format(e))
        try:
            exposedports=eval(image.exposedports)
            portmap={}
            
            for port in exposedports:
                out_port=randomport(port,server.host)
                portmap['{}/tcp'.format(port)]=out_port
            #分为有命令的run 和没有命令的run
            if image.command !="NoCommand":
                #有命令
                command=image.command
                container=client.containers.run(
                    image=image.RepoTags,
                    name=instance.containername,
                    command=command,
                    ports=portmap,
                    mem_limit=str(image.memli)+'m',
                    cpu_count=int(image.cpuli),
                    detach=True,
                    oom_kill_disable=True
                )
            else:
                #无命令
                container=client.containers.run(
                    image=image.RepoTags,
                    name=instance.containername,
                    ports=portmap,
                    mem_limit=str(image.memli)+'m',
                    cpu_count=int(image.cpuli),
                    detach=True,
                    oom_kill_disable=True
                )

            print("Instance Start! "+container.status)
            instance.startup=1
            instance.portmap=str(portmap)
            instance.host=server.host
            instance.containerid=container.id
            db.session.add(instance)
            db.session.commit()
    

            return json.dumps("success")
        except Exception as e:
            db.session.delete(instance)
            db.session.commit()
    
            return json.dumps("fail: {}".format(e))
    @classmethod
    def destroy_instance(cls,instanceid):
        instance=Instances.query.filter_by(id=instanceid).first()
        try:
            image=ChallengeImages.query.filter_by(id=instance.chaid).first()
            server=Servers.query.filter_by(tag=image.pullimage).first()
        except Exception as e:
            db.session.delete(instance)
            db.session.commit()
            return json.dumps("fail: {}".format(e))
        if server.tag=="local":
            try:
                client=docker.from_env()
            except Exception as e:
                
                return json.dumps("fail: {}".format(e))
        else:
            tls_config = docker.tls.TLSConfig(client_cert=(server.client_cert_file, server.client_key_file))
            try:
                client=docker.DockerClient(base_url=server.host,tls=tls_config)
            except Exception as e:
                return json.dumps("fail: {}".format(e))
        portmap=eval(instance.portmap)

        try:
            
            rm=client.containers.get(instance.containerid)
            rm.stop()
            rm.remove()
            db.session.delete(instance)
            db.session.commit()
    
            return json.dumps("Remove success!")
        except Exception as e:
            db.session.delete(instance)
            db.session.commit()
            return json.dumps("fail: container destroy error: {}".format(e))
    @classmethod
    def reload(cls,instanceid):
        instance=Instances.query.filter_by(id=instanceid).first()
        image=ChallengeImages.query.filter_by(id=instance.chaid).first()
        server=Servers.query.filter_by(tag=image.pullimage).first()
        if server.tag=="local":
            try:
                client=docker.from_env()
            except Exception as e:
                db.session.delete(instance)
                db.session.commit()
                return json.dumps("fail: {}".format(e))
        else:
            tls_config = docker.tls.TLSConfig(client_cert=(server.client_cert_file, server.client_key_file))
            try:
                client=docker.DockerClient(base_url=server.host,tls=tls_config)
            except Exception as e:
                db.session.delete(instance)
                db.session.commit()
                return json.dumps("fail: {}".format(e))
        try:
            rm=client.containers.get(instance.containerid)
            rm.stop()
            rm.remove()
            #分为有命令的run 和没有命令的run
            if image.command !="NoCommand":
                #有命令
                command=image.command
                container=client.containers.run(
                    image=image.RepoTags,
                    name=instance.containername,
                    command=command,
                    ports=portmap,
                    mem_limit=str(image.memli)+'m',
                    cpu_count=int(image.cpuli),
                    detach=True,
                    oom_kill_disable=True
                )
            else:
                #无命令
                container=client.containers.run(
                    image=image.RepoTags,
                    name=instance.containername,
                    ports=portmap,
                    mem_limit=str(image.memli)+'m',
                    cpu_count=int(image.cpuli),
                    detach=True,
                    oom_kill_disable=True
                )
            return json.dumps("Reload success!")
        except Exception as e:
            db.session.delete(instance)
            db.session.commit()
            return json.dumps("fail: container reload error: {}".format(e))

        
        
    