#-*- coding:utf-8 -*-
from flask import Blueprint, render_template, request,session
from CTFd.plugins import register_plugin_assets_directory
from CTFd.plugins.challenges import CHALLENGE_CLASSES,BaseChallenge
from CTFd.utils import user as current_user
from CTFd.utils.security.csrf import generate_nonce
from CTFd.utils.decorators import admins_only, authed_only
from CTFd.models import Challenges, Solves, db
from CTFd.utils.modes import get_model
from .models import *
from flask_apscheduler import APScheduler
from .utils import *
from .dockerutils import *
import sqlite3
import time
import docker
import datetime
import json
import hashlib
import os
import math


challenge_model = DynamicInstance




def load(app):
    app.db.create_all()
    page_blueprint = Blueprint(
        "dynamic_instance",
        __name__,
        template_folder="templates",
        static_folder="assets",
    )
    CHALLENGE_CLASSES["dynamic_instance"] = DynamicInstance #注册challenge类型
    register_plugin_assets_directory(app,"/plugins/dynamic_instance/assets")
    
    scheduler=APScheduler()
    scheduler.add_job(func=remove_timeout,id='remove_timeout',args=None,trigger='interval',seconds=60,replace_existing=True)
    scheduler.init_app(app=app)
    scheduler.start()

    @admins_only
    @page_blueprint.route('/config', methods=['GET','POST'])
    @admins_only
    def dynamic_instance_config():
        if request.method=="POST":
            form={} 
            for item in json.loads(request.get_data(as_text=True)):
                form[item['name']]=item['value']
            del form['nonce']
            with open("CTFd/plugins/dynamic_instance/plugin_config.json","w")as f:
                json.dump(form,f)
            if "docker" in form:
                client=docker.from_env()
                info=client.info()
                host=request.host
                if ":" in host:
                    host=host[0:host.index(':')]
                socket="None"
                Sys_os=info['OperatingSystem']
                num_cpu=info['NCPU']
                mem_total=int(int(info['MemTotal'])/1048576)
                num_img=info['Images']
                tag="local"
                client_cert_file,client_key_file="None","None"
                conn=sqlite3.connect("CTFd/ctfd.db")
                cusor=conn.cursor()
                cusor.execute("SELECT tag FROM servers WHERE id=1")
                isset=cusor.fetchone()
                if not isset:
                    cusor.execute(f"INSERT INTO servers (id,host,socket,tag,os,num_cpu,mem_total,num_img,client_cert_file,client_key_file) VALUES (1,'{host}','{socket}','{tag}','{Sys_os}',{num_cpu},{mem_total},{num_img},'{client_cert_file}','{client_key_file}');")
                    conn.commit()
                conn.close()
            else:
                conn=sqlite3.connect("CTFd/ctfd.db")
                cusor=conn.cursor()
                cusor.execute("DELETE FROM servers WHERE tag='local'")
                conn.commit()
                conn.close()
            return json.dumps("success!")
        conn=sqlite3.connect("CTFd/ctfd.db")
        cusor=conn.cursor()
        cusor.execute("SELECT * FROM challenge_images")
        challenge_images=cusor.fetchall()
        cusor.execute("SELECT * FROM servers")
        servers=cusor.fetchall()
        conn.commit()
        conn.close()
        return render_template('dynamic_instance.html',nonce=generate_nonce(),challenge_images=challenge_images,servers=servers)
    
    @page_blueprint.route('/new', methods=['POST','GET'])  
    @admins_only
    def dynamic_instance_new():
        form={} 
        for item in json.loads(request.get_data(as_text=True)):
            form[item['name']]=item['value']
        #print(form)
        if form['type']=="new_server":
            store_dir='CTFd/plugins/dynamic_instance/certs/'+hashlib.md5(form['cert'].encode('utf-8')).hexdigest()
            if os.path.exists(store_dir):
                delete(store_dir)
            os.mkdir(store_dir)
            client_cert_file=store_dir+'/cert.pem'
            with open(client_cert_file,'x') as f:
                f.write(form['cert'])
            client_key_file=store_dir+'/key.pem'
            with open(client_key_file,'x') as f:
                f.write(form['key'])
            socket=form['socket']
            host=socket.replace('tcp://','')
            host=host[0:host.index(':')]
            tls_config = docker.tls.TLSConfig(client_cert=(client_cert_file, client_key_file))
            try:
                client=docker.DockerClient(base_url=host,tls=tls_config)
            except:
                delete(store_dir)
                return json.dumps("fail: ConnectionRefusedError Check your host url or cert and key")
            info=client.info()
            Sys_os=info['OperatingSystem']
            num_cpu=info['NCPU']
            mem_total=int(int(info['MemTotal'])/1048576)
            num_img=info['Images']
            tag=form['tag']
            conn=sqlite3.connect("CTFd/ctfd.db")
            cusor=conn.cursor()
            cusor.execute(f"INSERT INTO servers (host,socket,tag,os,num_cpu,mem_total,num_img,client_cert_file,client_key_file) VALUES ('{host}','{socket}','{tag}','{Sys_os}',{num_cpu},{mem_total},{num_img},'{client_cert_file}','{client_key_file}');")
            conn.commit()
            conn.close()
            return json.dumps("success!")
        elif form['type']=="new_img":
            name=form['name']
            RepoTags=form['RepoTags']
            if ':' not in RepoTags:
                RepoTags=RepoTags+":latest"
            cpuli=form['cpuli']
            memli=form['memli']
            pullimage=form['pullimage']
            exposedports=form['exposedports']
            pulled=0
            created=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            size=0
            imageid="No Pulled yet"
            conn=sqlite3.connect("CTFd/ctfd.db")
            cusor=conn.cursor()
            cusor.execute(f"INSERT INTO challenge_images (name,RepoTags,imageid,created,size,exposedports,cpuli,memli,pullimage,pulled) VALUES ('{name}','{RepoTags}','{imageid}','{created}','{size}','{exposedports}',{cpuli},{memli},'{pullimage}',{pulled});")
            conn.commit()
            conn.close()
            scheduler.add_job(func=pull_image, args=(pullimage,RepoTags), trigger='date',next_run_time=datetime.datetime.now() + datetime.timedelta(seconds=5), id='pullimage',replace_existing=True)
  
            #pull_image(pullimage,RepoTags)
            return json.dumps("success!")
        return json.dumps("Nothing")
    @page_blueprint.route('/delserver/<int:server_id>', methods=['DELETE'])  
    @admins_only
    def delserver(server_id):
        server=Servers.query.filter_by(id=server_id).first()
        db.session.delete(server)
        db.session.commit()
        return json.dumps("Delete!")
    @page_blueprint.route('/delimage/<int:image_id>', methods=['DELETE'])  
    @admins_only
    def delimage(image_id):
        image=ChallengeImages.query.filter_by(id=image_id).first()
        db.session.delete(image)
        db.session.commit()
        return json.dumps("Delete!")

    @authed_only
    @page_blueprint.route('/instanceinfo/<int:challenge_id>', methods=['GET'])
    def instanceinfo(challenge_id):
        result={"type":""}
        userid=current_user.get_current_user_attrs().id
        instance=Instances.query.filter_by(userid=userid,chaid=challenge_id).first()
        if instance:
            if instance.startup:
                result['type']="booted"
                result['starttime']=instance.starttime
                result['endtime']=instance.endtime
                result['host']=instance.host
                result['portmap']=eval(instance.portmap)
                if result['portmap']['80/tcp']:
                    result['host']="http://"+result['host']+":"+str(result['portmap']['80/tcp'])
                return json.dumps(result)

            else:
                result['type']="booting"
                return json.dumps(result)
        else:
            result['type']="notboot"
        return json.dumps(result)
    @authed_only
    @page_blueprint.route('/bootinstance/<int:challenge_id>', methods=['GET'])
    def bootinstance(challenge_id):
        print("bootinstance")
        userid=current_user.get_current_user_attrs().id
        had=Instances.query.filter_by(userid=userid).first()
        if had:
            return json.dumps("You can only have one instance at the same time!")
        config=load_config()
        chal=DynamicInstanceChallenge.query.filter_by(id=challenge_id).first()
        chaid=chal.id
        starttime=time.time()
        endtime=time.time()+(int(config['survtime'])*60)
        
        startup=0
        imagename=chal.ChallengeImageName
        containername=f"{chaid}_{userid}_{imagename}"
        containerid=""#在实例启动时赋值
        host=""#在实例启动时赋值
        portmap=""#在实例启动时赋值
        new_instance=Instances(chaid,starttime,endtime,userid,startup,imagename,containername,containerid,host,portmap)
        db.session.add(new_instance)
        db.session.commit()
        #开始启动docker容器
        result=Instance.bootinstance(imagename,new_instance.id)
        return result
    @authed_only
    @page_blueprint.route('/destroyinstance/<int:challenge_id>', methods=['GET'])
    def destroyinstance(challenge_id):
        userid=current_user.get_current_user_attrs().id
        instance=Instances.query.filter_by(chaid=challenge_id,userid=userid).first()
        result=Instance.destroy_instance(instance.id)
        return result
    @authed_only
    @page_blueprint.route('/exttime/<int:challenge_id>', methods=['GET'])
    def exttime(challenge_id):
        userid=current_user.get_current_user_attrs().id
        instance=Instances.query.filter_by(chaid=challenge_id,userid=userid).first()
        config=load_config()
        instance.endtime=str(float(instance.endtime)+float(config['exttime'])*60)
        if (float(instance.endtime)-float(instance.starttime))>=(float(config['maxsurtime'])*60):
            return json.dumps("Max survice time!")
        else:
            db.session.add(instance)
            db.session.commit()
            return json.dumps('More Time')
    @authed_only
    @page_blueprint.route('/reload/<int:challenge_id>', methods=['GET'])
    def reload(challenge_id):
        userid=current_user.get_current_user_attrs().id
        instance=Instances.query.filter_by(chaid=challenge_id,userid=userid).first()
        result=Instance.reload(instance.id)
        return result
    app.register_blueprint(page_blueprint,url_prefix='/plugins/dynamic_instance')