import docker
from CTFd.models import Challenges, db
from .models import *
import random

def randomport(port,serverid):
    if port == 80:
        out_port=random.randint(8000,8999)
        occupy=PortOccupy.query.filter_by(port=out_port,serverid=serverid).first()
        if occupy:
            randomport(port,serverid)
        else:
            occupy=PortOccupy(serverid,out_port)
            db.session.add(occupy)
            db.session.commit()
    
            return out_port
    else:
        out_port=random.randint(20000,30000)
        occupy=PortOccupy.query.filter_by(port=out_port,serverid=serverid).first()
        if occupy:
            randomport(port,serverid)
        else:
            occupy=PortOccupy(serverid,out_port)
            db.session.add(occupy)
            db.session.commit()
    
            return out_port

class Instance:
    
    @classmethod
    def bootinstance(cls,imagename,instanceid):
        print("booting instance")
        result=""
        image=ChallengeImages.query.filter_by(name=imagename).first()
        server=Servers.query.filter_by(tag=image.pullimage).first()
        instance=Instances.query.filter_by(id=instanceid).first()
        #开始加载docker容器 分两种情况,本地服务器与远程服务器
        if server.tag=="local":
            try:
                client=docker.from_env()
            except:
                db.session.delete(instance)
                db.session.commit()
        
                return json.dumps("fail: config error")
        else:
            tls_config = docker.tls.TLSConfig(client_cert=(server.client_cert_file, server.client_key_file))
            try:
                client=docker.DockerClient(base_url=server.socket,tls=tls_config)
            except:
                db.session.delete(instance)
                db.session.commit()
                return json.dumps("fail: config error")
        try:
            exposedports=eval(image.exposedports)
            portmap={}
            for port in exposedports:
                out_port=randomport(port,server.id)
                portmap['{}/tcp'.format(port)]=out_port
            container=client.containers.run(
                image=image.RepoTags,
                name=instance.containername,
                ports=portmap,
                mem_limit=str(image.memli)+'m',
                cpu_count=int(image.cpuli),
                detach=True
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
        image=ChallengeImages.query.filter_by(name=instance.imagename).first()
        server=Servers.query.filter_by(tag=image.pullimage).first()
        if server.tag=="local":
            try:
                client=docker.from_env()
            except:
                return json.dumps("fail: config error")
        else:
            tls_config = docker.tls.TLSConfig(client_cert=(server.client_cert_file, server.client_key_file))
            try:
                client=docker.DockerClient(base_url=server.host,tls=tls_config)
            except:
                return json.dumps("fail: config error")
        portmap=eval(instance.portmap)
        for port in portmap:
            occupy=PortOccupy.query.filter_by(port=portmap[port],serverid=server.id).delete()
            db.session.commit()

        try:
            rm=client.containers.get(instance.containerid)
            rm.stop()
            rm.remove()
            db.session.delete(instance)
            db.session.commit()
    
            return json.dumps("Remove success!")
        except Exception as e:
                return json.dumps("fail: container destroy error: {}".format(e))
    @classmethod
    def reload(cls,instanceid):
        instance=Instances.query.filter_by(id=instanceid).first()
        image=ChallengeImages.query.filter_by(name=instance.imagename).first()
        server=Servers.query.filter_by(tag=image.pullimage).first()
        if server.tag=="local":
            try:
                client=docker.from_env()
            except:
                return json.dumps("fail: config error")
        else:
            tls_config = docker.tls.TLSConfig(client_cert=(server.client_cert_file, server.client_key_file))
            try:
                client=docker.DockerClient(base_url=server.host,tls=tls_config)
            except:
                return json.dumps("fail: config error")
        try:
            rm=client.containers.get(instance.containerid)
            rm.stop()
            rm.remove()
            container=client.containers.run(
                image=image.RepoTags,
                name=instance.containername,
                ports=eval(instance.portmap),
                mem_limit=str(image.memli)+'m',
                cpu_count=int(image.cpuli),
                detach=True
            )
            instance.containerid=container.id
            db.session.add(instance)
            db.session.commit()
    
            
            return json.dumps("Reload success!")
        except Exception as e:
                return json.dumps("fail: container reload error: {}".format(e))

        
        
    