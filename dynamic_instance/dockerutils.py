import docker
from CTFd.models import Challenges, db
from .models import *
import random
import os 
import socket
import json

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
    #创建实例
    @classmethod
    def bootinstance(cls,imagename,instanceid):
        print("booting instance")        
        try:
            instance=Instances.query.filter_by(id=instanceid).first()
            image=ChallengeImages.query.filter_by(name=imagename).first()
            server=Servers.query.filter_by(tag=image.pullimage).first()
        #开始加载docker容器 分两种情况,本地服务器与远程服务器
            if server.tag=="local":
                client=docker.from_env()
            else:
                tls_config = docker.tls.TLSConfig(client_cert=(server.client_cert_file, server.client_key_file))
                client=docker.DockerClient(base_url=server.socket,tls=tls_config)
            exposedports=eval(image.exposedports)
            portmap={}
            #如果存在同名容器报错
            try:
                client.containers.get(instance.containername)
                db.session.delete(instance)
                db.session.commit()
                return json.dumps("Containner exists!Please contact with admin!")
            except:
                for port in exposedports:
                    out_port=randomport(port,server.host)
                    portmap['{}/tcp'.format(port)]=out_port
            
                container=client.containers.run(
                    image=image.RepoTags,
                    name=instance.containername,
                    ports=portmap,
                    mem_limit=str(image.memli)+'m',
                    cpu_count=int(int(image.cpuli)*1e9),
                    detach=True,
                    tty=True,
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
    #销毁实例
    @classmethod
    def destroy_instance(cls,instanceid):
        
        try :
            instance=Instances.query.filter_by(id=instanceid).first()
            image=ChallengeImages.query.filter_by(name=instance.imagename).first()
            server=Servers.query.filter_by(tag=image.pullimage).first()
            if server.tag=="local":
                client=docker.from_env()
            else:
                tls_config = docker.tls.TLSConfig(client_cert=(server.client_cert_file, server.client_key_file))
                client=docker.DockerClient(base_url=server.socket,tls=tls_config)
            try:
                rm=client.containers.get(instance.containername)
            except:
                db.session.delete(instance)
                db.session.commit()
                return json.dumps("Containner not exists!Please contact with admin!")
            rm.stop()
            rm.remove()
            db.session.delete(instance)
            db.session.commit()
            return json.dumps("Remove success!")
        except Exception as e:
            print(e)
            '''try:#尝试从本地删除容器
                instance=Instances.query.filter_by(id=instanceid).first()
                client=docker.from_env()
                rm=client.containers.get(instance.containername)
                rm.stop()
                rm.remove()
            except Exception as e:
                print(e)'''
            db.session.delete(instance)
            db.session.commit()
            return json.dumps("fail: container destroy error: {}".format(e))
    #重载实例
    @classmethod
    def reload(cls,instanceid):
        try:
            instance=Instances.query.filter_by(id=instanceid).first()
            image=ChallengeImages.query.filter_by(name=instance.imagename).first()
            server=Servers.query.filter_by(tag=image.pullimage).first()
            if server.tag=="local":
                client=docker.from_env()
            else:
                tls_config = docker.tls.TLSConfig(client_cert=(server.client_cert_file, server.client_key_file))
                client=docker.DockerClient(base_url=server.socket,tls=tls_config)
            portmap=eval(instance.portmap)
            try:
                rm=client.containers.get(instance.containerid)
                rm.stop()
                rm.remove()
            except Exception as e:
                    db.session.delete(instance)
                    db.session.commit()
                    return json.dumps("Containner not exists!Please contact with admin!")

            container=client.containers.run(
                    image=image.RepoTags,
                    name=instance.containername,
                    ports=portmap,
                    mem_limit=str(image.memli)+'m',
                    cpu_count=int(int(image.cpuli)*1e9),
                    detach=True,
                    tty=True,
                    oom_kill_disable=True
                )
            return json.dumps("Reload success!")
        except Exception as e:
            db.session.delete(instance)
            db.session.commit()
            return json.dumps("fail: container reload error: {}".format(e))
    #检查镜像是否本地存在
    '''@classmethod
    def search_local(cls,pullimage,RepoTags):
        try:
            server=Servers.query.filter_by(tag=image.pullimage).first()
            if server.tag=="local":
                client=docker.from_env()
            else:
                tls_config = docker.tls.TLSConfig(client_cert=(server.client_cert_file, server.client_key_file))
                client=docker.DockerClient(base_url=server.socket,tls=tls_config)
            #判断是否在本地
            if client.images.list(name=RepoTags):
                return True
            else:
                return False
        except Exception as e:
            return False
        '''