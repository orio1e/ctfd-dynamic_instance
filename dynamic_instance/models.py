from flask import Blueprint, render_template, request,session
from CTFd.plugins import register_plugin_assets_directory
from CTFd.plugins.challenges import CHALLENGE_CLASSES,BaseChallenge
from CTFd.utils import user as current_user
from CTFd.utils.security.csrf import generate_nonce
from CTFd.utils.decorators import admins_only, authed_only
from CTFd.models import Fails,Flags,Challenges,ChallengeFiles,Tags,Hints, Solves, db
from CTFd.utils.modes import get_model
from CTFd.plugins.flags import get_flag_class
from CTFd.utils.uploads import delete_file
from CTFd.utils.user import get_ip
import sqlite3
import time
import docker
import json
import hashlib
import os
import math

#服务器
class Servers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    host = db.Column(db.VARCHAR(128))
    socket = db.Column(db.VARCHAR(128))
    tag = db.Column(db.VARCHAR(128))
    os = db.Column(db.VARCHAR(128))
    num_cpu = db.Column(db.Integer)
    mem_total = db.Column(db.Integer)
    num_img = db.Column(db.Integer)
    client_cert_file=db.Column(db.VARCHAR(128))
    client_key_file=db.Column(db.VARCHAR(128))

    def __init__(self, host,tag,os,num_cpu,mem_total,num_img,client_cert_file,client_key_file):
        self.host = host
        self.tag = tag
        self.os=os
        self.num_cpu=num_cpu
        self.mem_total=mem_total
        self.num_img=num_img
        self.client_cert_file=client_cert_file
        self.client_key_file=client_key_file
#题目镜像
class ChallengeImages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.VARCHAR(128))
    RepoTags = db.Column(db.VARCHAR(128))
    imageid = db.Column(db.VARCHAR(128))
    created = db.Column(db.VARCHAR(128))
    size=db.Column(db.Integer)
    exposedports=db.Column(db.VARCHAR(128))
    cpuli = db.Column(db.Integer)
    memli=db.Column(db.Integer)
    pullimage=db.Column(db.VARCHAR(128))
    pulled=db.Column(db.Integer)
    pullimage=db.Column(db.VARCHAR(128))

    def __init__(self,name, RepoTags,imageid, created,cpuli,memli,pullimage,size,exposedports):
        self.name = name
        self.RepoTags = RepoTags
        self.imageid = imageid
        self.created = created
        self.size = size
        self.exposedports=exposedports
        self.cpuli = cpuli
        self.memli = memli
        self.pullimage=pullimage
#实例
class Instances(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chaid=db.Column(db.Integer)
    starttime=db.Column(db.VARCHAR(128))
    endtime=db.Column(db.VARCHAR(128))
    userid=db.Column(db.VARCHAR(128))
    startup=db.Column(db.Integer)
    imagename=db.Column(db.VARCHAR(128))
    containername=db.Column(db.VARCHAR(128))
    containerid=db.Column(db.VARCHAR(128))
    host=db.Column(db.VARCHAR(128))#only ip
    portmap=db.Column(db.VARCHAR(128))#python dict
    def __init__(self,chaid,starttime,endtime,userid,startup,imagename,containername,containerid,host,portmap):
        self.chaid=chaid
        self.starttime = starttime
        self.endtime = endtime
        self.userid = userid
        self.startup=startup
        self.imagename = imagename
        self.containername = containername
        self.containerid = containerid
        self.host = host
        self.portmap = portmap
        
#动态靶机挑战类型
class DynamicInstanceChallenge(Challenges):
    __mapper_args__ = {"polymorphic_identity": "dynamic_instance"}
    id = db.Column(db.Integer,db.ForeignKey("challenges.id"),primary_key=True)
    ChallengeImageName=db.Column(db.VARCHAR(128))
    #分数相关
    initial=db.Column(db.Float)
    per_decay=db.Column(db.Float)
    minimum=db.Column(db.Float)
    def __init__(self, *args, **kwargs):
        super(DynamicInstanceChallenge, self).__init__(**kwargs)
        self.initial = float(kwargs["value"])

class DynamicInstance(BaseChallenge):
    id = "dynamic_instance"  # Unique identifier used to register challenges
    name = "dynamic_instance"  # Name of a challenge type
    templates = {  # Handlebars templates used for each aspect of challenge editing & viewing
        "create": "/plugins/dynamic_instance/assets/create.html",
        "update": "/plugins/dynamic_instance/assets/update.html",
        "view": "/plugins/dynamic_instance/assets/view.html",
    }
    scripts = {  # Scripts that are loaded when a template is loaded
        "create": "/plugins/dynamic_instance/assets/create.js",
        "update": "/plugins/dynamic_instance/assets/update.js",
        "view": "/plugins/dynamic_instance/assets/view.js",
    }
    @classmethod
    def calculate_value(cls, challenge):
        Model = get_model()

        solve_count = (
            Solves.query.join(Model, Solves.account_id == Model.id)
            .filter(
                Solves.challenge_id == challenge.id,
                Model.hidden == False,
                Model.banned == False,
            )
            .count()
        )

        # If the solve count is 0 we shouldn't manipulate the solve count to
        # let the math update back to normal
        if solve_count != 0:
            # We subtract -1 to allow the first solver to get max point value
            solve_count -= 1

        
        value = ((challenge.initial)-(challenge.per_decay)*solve_count)
        if value<challenge.minimum:
            value=challenge.minimum

        value = math.ceil(float(value))

        challenge.value = value
        db.session.commit()

        return challenge

    
    @classmethod
    def read(cls, challenge):
        """
        This method is in used to access the data of a challenge in a format processable by the front end.

        :param challenge:
        :return: Challenge object, data dictionary to be returned to the user
        """
        challenge = DynamicInstanceChallenge.query.filter_by(id=challenge.id).first()
        data = {
            "id": challenge.id,
            "name": challenge.name,
            "value": challenge.value,
            "initial":challenge.initial,
            "minimum": challenge.minimum,
            "description": challenge.description,
            "category": challenge.category,
            "state": challenge.state,
            "max_attempts": challenge.max_attempts,
            "type": challenge.type,
            "ChallengeImageName":challenge.ChallengeImageName,
            "per_decay":challenge.per_decay,
            "type_data": {
                "id": cls.id,
                "name": cls.name,
                "templates": cls.templates,
                "scripts": cls.scripts,
            },
        }
        return data

    @classmethod
    def update(cls, challenge, request):
        """
        This method is used to update the information associated with a challenge. This should be kept strictly to the
        Challenges table and any child tables.

        :param challenge:
        :param request:
        :return:
        """
        data = request.form or request.get_json()

        for attr, value in data.items():
            # We need to set these to floats so that the next operations don't operate on strings
            if attr in ("initial", "minimum", "per_decay"):
                value = float(value)
            setattr(challenge, attr, value)

        return DynamicInstance.calculate_value(challenge)

    @classmethod
    def solve(cls, user, team, challenge, request):
        super().solve(user, team, challenge, request)

        DynamicInstance.calculate_value(challenge)
    @staticmethod
    def create(request):
        """
        This method is used to process the challenge creation request.

        :param request:
        :return:
        """
        data = request.form or request.get_json()
        data['minimum']=float(data['minimum'])
        data['per_decay']=float(data['per_decay'])
        challenge = DynamicInstanceChallenge(**data)

        db.session.add(challenge)
        db.session.commit()


        return challenge
    @staticmethod
    def delete(challenge):
        """
        This method is used to delete the resources used by a challenge.

        :param challenge:
        :return:
        """
        Fails.query.filter_by(challenge_id=challenge.id).delete()
        Solves.query.filter_by(challenge_id=challenge.id).delete()
        Flags.query.filter_by(challenge_id=challenge.id).delete()
        files = ChallengeFiles.query.filter_by(challenge_id=challenge.id).all()
        for f in files:
            delete_file(f.id)
        ChallengeFiles.query.filter_by(challenge_id=challenge.id).delete()
        Tags.query.filter_by(challenge_id=challenge.id).delete()
        Hints.query.filter_by(challenge_id=challenge.id).delete()
        DynamicInstanceChallenge.query.filter_by(id=challenge.id).delete()
        Challenges.query.filter_by(id=challenge.id).delete()
        db.session.commit()

        return 



