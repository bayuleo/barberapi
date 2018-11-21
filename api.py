from flask import Flask, request
from flask_restful import reqparse, abort, Api, Resource, fields, marshal
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_jwt_extended import *
from flask_cors import CORS
import sys, requests

app = Flask(__name__)
api = Api(app)
CORS(app)

#sql Alchemy Conf

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456789@barbers.cetzg8vhm6ub.us-east-2.rds.amazonaws.com/barbers'
app.config['SQLALCHEMY_ECHO'] = True

#SQL Migrate
db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

#JWT
app.config['JWT_SECRET_KEY']='bayu_barber'
jwt=JWTManager(app)

#create Model

user_field = {
    'user_id' : fields.Integer,
    'name' : fields.String,
    'username' : fields.String,
    'password' : fields.String,
    'email' : fields.String,
    'user_key' : fields.String,
    'user_secret' : fields.String,
    'status' : fields.Boolean,
    'type' : fields.String
}

item_field = {
    'item_id' : fields.Integer,
    'name' : fields.String,
    'location' : fields.String,
    'category_gender' : fields.String,
    'time_open' : fields.String,
    'time_close' : fields.String,
    'duration_service' : fields.Integer,
    'quota' : fields.Integer,
    'image_url' : fields.String,
    'price' : fields.Integer,
    'user_id' : fields.Integer,
    'jalan' : fields.String,
    'kelurahan' : fields.String,
    'kecamatan' : fields.String,
    'kota' : fields.String,
    'provinsi' : fields.String,
    'kode_pos' : fields.String,
    'rating' : fields.Integer
}

order_field = {
    'order_id' : fields.Integer,
    'user_id' : fields.Integer,
    'item_id' : fields.Integer,
    'date_order' : fields.String,
    'time_order' : fields.String,
    'quota_left' : fields.Integer
}

class Users(db.Model) :
    user_id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(255), nullable = False)
    username = db.Column(db.String(255), nullable = False, unique = True)
    password = db.Column(db.String(255), nullable = False)
    email = db.Column(db.String(255), nullable = False)
    user_key = db.Column(db.String(30), unique = True, nullable = False)
    user_secret = db.Column(db.String(255), nullable = False)
    status = db.Column(db.Boolean, nullable = True)
    type = db.Column(db.String(100), nullable = True)
    
    def __init__(self, name, username, password, email, user_key, user_secret, status = 1, type = "public") :
        self.name=name
        self.username=username
        self.password=password
        self.email=email
        self.user_key=user_key
        self.user_secret=user_secret
        self.status=status
        self.type=type

    def __repr__(self):
        return '<Users %r>' % self.user_id

class Items(db.Model) :
    item_id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(255), nullable = False)
    location = db.Column(db.String(255), nullable = False)
    category_gender = db.Column(db.String(255), nullable = True)
    time_open = db.Column(db.String(255), nullable = False)
    time_close = db.Column(db.String(30), nullable = False)
    duration_service = db.Column(db.Integer, nullable = False)
    quota = db.Column(db.Integer, nullable = False)
    image_url = db.Column(db.String(255), nullable = False)
    price = db.Column(db.Integer, nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable = False)
    jalan = db.Column(db.String(255), nullable = False)
    kelurahan = db.Column(db.String(255), nullable = False) 
    kecamatan = db.Column(db.String(255), nullable = False)
    kota = db.Column(db.String(255), nullable = False)
    provinsi =  db.Column(db.String(255), nullable = False)
    kode_pos = db.Column(db.String(255), nullable = False)
    rating = db.Column(db.Integer, nullable = False)

    def __init__(self, name, location, category_gender, time_open, time_close, duration_service, quota, image_url, price, user_id, jalan, kelurahan, kecamatan, kota, provinsi, kode_pos, rating) :
        self.name = name
        self.location = location
        self.category_gender = category_gender
        self.time_open = time_open
        self.time_close = time_close
        self.duration_service = duration_service
        self.quota = quota
        self.image_url = image_url
        self.price = price
        self.user_id = user_id
        self.jalan = jalan
        self.kelurahan = kelurahan
        self.kecamatan = kecamatan
        self.kota = kota
        self.provinsi = provinsi       
        self.kode_pos = kode_pos
        self.rating = rating

    def __repr__(self):
        return '<Items %r>' % self.items_id

class Orders(db.Model) :
    order_id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, nullable = False)
    item_id = db.Column(db.Integer, nullable = False)
    date_order = db.Column(db.Date, nullable = False)
    time_order = db.Column(db.Time, nullable = False)
    quota_left = db.Column(db.Integer, nullable = False)
    
    
    def __init__(self, user_id, item_id, date_order, time_order, quota_left) :
        self.user_id = user_id
        self.item_id = item_id
        self.date_order = date_order
        self.time_order = time_order
        self.quota_left = quota_left


    def __repr__(self):
        return '<Orders %r>' % self.order_id

class UserResource(Resource) :
    # @jwt_required
    def get(self) :
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, location='args')
        parser.add_argument('p', type=int, default=1, location='args')
        parser.add_argument('rp', type=int, default=25,location='args')
        parser.add_argument('name', type=str, location='args')
        parser.add_argument('username', type=str, location='args')
        parser.add_argument('orderby', location='args', help='invalid orderby value', choices=('user_id', 'name', 'username', 'email'))
        parser.add_argument('sort', default='asc', location='args', help='invalid sort value', choices=('desc', 'asc'))
        args=parser.parse_args()
        
        #Filter
        if args['p'] == 1 :
            offset = 0
        else :
            offset = (args['p'] * args['rp']) - args['rp']
        qry = Users.query

        if args['id'] :
            qry=qry.filter_by(user_id=args['id'])

        if args['name'] :
            qry=qry.filter_by(name=args['name'])

        if args['username'] :
            qry=qry.filter_by(username=args['username'])

        sort=args['sort']
        if args['orderby'] == 'user_id' :
            qry=qry.order_by('user_id %s' % (sort))
        elif args['orderby'] == 'name' :
            qry=qry.order_by('name %s' % (sort))
        elif args['orderby'] == 'username' :
            qry=qry.order_by('username %s' % (sort))
        elif args['orderby'] == 'email' :
            qry=qry.order_by('email %s' % (sort))

        qry = qry.limit(args['rp']).offset(offset)    

        rows = []
        for row in qry.all():
            rows.append(marshal(row, user_field))
        return rows, 200

    # @jwt_required
    def post(self) :
        parser = reqparse.RequestParser ()
        parser.add_argument ('name',type=str, help = 'Must be str',location='json',required = True)
        parser.add_argument ('username',type=str, help = 'Must be str',location='json',required = True)
        parser.add_argument ('password',type=str, help = 'Must be str',location='json',required = True)
        parser.add_argument ('email',type=str, help = 'Must be str',location='json',required = True)
        parser.add_argument ('user_key', type=str, help = 'Must be str',location='json',required = True)
        parser.add_argument ('user_secret', type=str, help = 'Must be str',location='json',required = True)
        parser.add_argument ('status', type=bool, help = 'Must be boolean',location='json',required = False, default = True)
        parser.add_argument ('type', type=str, help = 'Must be str',location='json',required = False)
        
        
        args =  parser.parse_args ()
        insert = Users(name = args['name'], username = args['username'], password = args['password'], email = args['email'], user_key = args['user_key'], user_secret = args['user_secret'], status = args['status'], type = args['type'])
        db.session.add(insert)
        db.session.commit()
        return marshal(insert, user_field), 201
        
    # @jwt_required
    def put(self, id) :
        parser = reqparse.RequestParser()
        parser.add_argument ('name',type=str, help = 'Must be str',location='json',required = True)
        parser.add_argument ('username',type=str, help = 'Must be str',location='json',required = True)
        parser.add_argument ('password',type=str, help = 'Must be str',location='json',required = True)
        parser.add_argument ('email',type=str, help = 'Must be str',location='json',required = True)
        parser.add_argument ('user_key', type=str, help = 'Must be str',location='json',required = True)
        parser.add_argument ('user_secret', type=str, help = 'Must be str',location='json',required = True)
        parser.add_argument ('status', type=bool, help = 'Must be boolean',location='json',required = False, default = True)
        parser.add_argument ('type', type=str, help = 'Must be str',location='json',required = False)
        args = parser.parse_args()


        Users.query.filter_by(user_id = id).update(dict(
            name=args['name'],
            username=args['username'],
            password=args['password'],
            email=args['email'],
            user_key=args['user_key'],
            user_secret=args['user_secret'],
            status=args['status'],
            type=args['type']
            ))
        db.session.commit()

        #Get Data
        qry = Users.query.filter_by(user_id=id)
        rows = []
        for row in qry.all():
            rows.append(marshal(row, user_field))
        if rows :
            return rows, 200
        else :
            return {'message' : 'NOT_FOUND'}, 404

    # @jwt_required
    def delete(self) :
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, required=True, help="ID User Kosong!",location='args')
        args = parser.parse_args()
        qry = Users.query.filter_by(user_id = args['id'])
        rows = []
        for row in qry.all():
            rows.append(marshal(row, user_field))
        if rows :
            Users.query.filter_by(user_id=args['id']).delete()
            db.session.commit()
            return rows, 200
        else :
            return {'message' : 'NOT_FOUND'}, 404

class MeResource(Resource) :

    @jwt_required
    def get(self):
       user_id=get_jwt_identity()
       qry = Users.query
       qry = qry.filter_by(user_id=user_id)
       qry = marshal(qry.all(), user_field)
       return qry, 200


class ItemResource(Resource) :
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, location='args')
        parser.add_argument('p', type=int, default=1, location='args')
        parser.add_argument('rp', type=int, default=25,location='args')
        parser.add_argument('name', type=str, location='args')
        parser.add_argument('kota', type=str, location='args')
        parser.add_argument('user_id', type=str, location='args')
        parser.add_argument('category_gender', type=str, location='args')
        parser.add_argument('orderby', location='args', help='invalid orderby value', choices=('duration_service', 'quota', 'price'))
        parser.add_argument('sort', default='asc', location='args', help='invalid sort value', choices=('desc', 'asc'))
        args=parser.parse_args()
        
        #Pagination
        if args['p'] == 1 :
            offset = 0
        else :
            offset = (args['p'] * args['rp']) - args['rp']
        qry = Items.query

        #Filter
        if args['id'] :
            qry=qry.filter_by(item_id=args['id'])

        if args['name'] :
            qry=qry.filter_by(name=args['name'])

        if args['category_gender'] :
            qry=qry.filter_by(category_gender=args['category_gender'])

        if args['kota'] :
            qry=qry.filter_by(kota=args['kota'])

        if args['user_id'] :
            qry=qry.filter_by(user_id=args['user_id'])

        sort=args['sort']
        if args['orderby'] == 'duration_service' :
            qry=qry.order_by('duration_service %s' % (sort))
        elif args['orderby'] == 'quota' :
            qry=qry.order_by('quota %s' % (sort))
        elif args['orderby'] == 'price' :
            qry=qry.order_by('price %s' % (sort))

        qry = qry.limit(args['rp']).offset(offset)    

        rows = []
        for row in qry.all():
            rows.append(marshal(row, item_field))
        return rows, 200
    
    @jwt_required
    def post(self):
        verify_jwt_in_request()
        claims = get_jwt_claims()
        parser = reqparse.RequestParser ()
        parser.add_argument ('name',type=str, help = 'Must be str',location='json',required = True)
        parser.add_argument ('location',type=str, help = 'Must be str',location='json',required = True)
        parser.add_argument ('category_gender',type=str, help = 'Must be str',location='json',required = True)
        parser.add_argument ('time_open',type=str, help = 'Must be str',location='json',required = True)
        parser.add_argument ('time_close', type=str, help = 'Must be str',location='json',required = True)
        parser.add_argument ('duration_service', type=int, help = 'Must be int',location='json',required = True)
        parser.add_argument ('quota', type=int, help = 'Must be int',location='json',required = True)
        parser.add_argument ('image_url', type=str, help = 'Must be str',location='json',required = True)
        parser.add_argument ('price', type=int, help = 'Must be int',location='json',required = True)
        parser.add_argument ('jalan', type=str, help = 'Must be str', location='json', required = True)
        parser.add_argument ('kelurahan', type=str, help = 'Must be str', location='json', required = True)
        parser.add_argument ('kecamatan', type=str, help = 'Must be str', location='json', required = True)
        parser.add_argument ('kota', type=str, help = 'Must be str', location='json', required = True)
        parser.add_argument ('provinsi', type=str, help = 'Must be str', location='json', required = True)
        parser.add_argument ('kode_pos', type=str, help = 'Must be str', location='json', required = True)
        parser.add_argument ('rating', type=int, help = 'Must be int', location='json', required = True)        
        args =  parser.parse_args ()
        insert = Items(name = args['name'], location = args['location'], category_gender = args['category_gender'], time_open = args['time_open'], time_close = args['time_close'], duration_service = args['duration_service'], quota = args['quota'], image_url = args['image_url'], price = args['price'], user_id = claims['user_id'], jalan = args['jalan'] , kelurahan = args['kelurahan'] , kecamatan = args['kecamatan'] , kota = args['kota'] , provinsi = args['provinsi'] , kode_pos = args['kode_pos'] , rating = args['rating'])
        db.session.add(insert)
        db.session.commit()
        return marshal(insert, item_field), 201

    def put(self, id):
        parser = reqparse.RequestParser ()
        parser.add_argument ('name',type=str, help = 'Must be str',location='json',required = True)
        parser.add_argument ('location',type=str, help = 'Must be str',location='json',required = True)
        parser.add_argument ('category_gender',type=str, help = 'Must be str',location='json',required = True)
        parser.add_argument ('time_open',type=str, help = 'Must be str',location='json',required = True)
        parser.add_argument ('time_close', type=str, help = 'Must be str',location='json',required = True)
        parser.add_argument ('duration_service', type=int, help = 'Must be int',location='json',required = True)
        parser.add_argument ('quota', type=int, help = 'Must be int',location='json',required = True)
        parser.add_argument ('image_url', type=str, help = 'Must be str',location='json',required = True)
        parser.add_argument ('price', type=int, help = 'Must be int',location='json',required = True)
        parser.add_argument ('user_id', type=str, help = 'Must be str',location='json',required = True)
        args =  parser.parse_args ()
        
        Items.query.filter_by(item_id = id).update(dict(
            name=args['name'],
            location=args['location'],
            category_gender=args['category_gender'],
            time_open=args['time_open'],
            time_close=args['time_close'],
            duration_service=args['duration_service'],
            quota=args['quota'],
            image_url=args['image_url'],
            price=args['price'],
            user_id=args['user_id']
            ))
        db.session.commit()

        #Get Data
        qry = Items.query.filter_by(item_id=id)
        rows = []
        for row in qry.all():
            rows.append(marshal(row, item_field))
        if rows :
            return rows, 200
        else :
            return {'message' : 'NOT_FOUND'}, 404

    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, required=True, help="ID Item Kosong!",location='args')
        args = parser.parse_args()
        qry = Items.query.filter_by(item_id = args['id'])
        rows = []
        for row in qry.all():
            rows.append(marshal(row, item_field))
        if rows :
            Items.query.filter_by(item_id=args['id']).delete()
            db.session.commit()
            return rows, 200
        else :
            return {'message' : 'NOT_FOUND'}, 404

class OrderResource(Resource) :
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, location='args')
        parser.add_argument('p', type=int, default=1, location='args')
        parser.add_argument('rp', type=int, default=25,location='args')
        parser.add_argument('user_id', type=str, location='args')
        parser.add_argument('item_id', type=str, location='args')
        parser.add_argument('orderby', location='args', help='invalid orderby value', choices=('date_order', 'time_order', 'quota_left'))
        parser.add_argument('sort', default='asc', location='args', help='invalid sort value', choices=('desc', 'asc'))
        args=parser.parse_args()
        
        #Filter
        if args['p'] == 1 :
            offset = 0
        else :
            offset = (args['p'] * args['rp']) - args['rp']
        qry = Orders.query

        if args['id'] :
            qry=qry.filter_by(order_id=args['id'])

        if args['user_id'] :
            qry=qry.filter_by(user_id=args['user_id'])

        if args['item_id'] :
            qry=qry.filter_by(item_id=args['item_id'])

        sort=args['sort']
        if args['orderby'] == 'date_order' :
            qry=qry.order_by('date_order %s' % (sort))
        elif args['orderby'] == 'time_order' :
            qry=qry.order_by('time_order %s' % (sort))
        elif args['orderby'] == 'quota_left' :
            qry=qry.order_by('quota_left %s' % (sort))

        qry = qry.limit(args['rp']).offset(offset)    

        rows = []
        for row in qry.all():
            rows.append(marshal(row, order_field))
        return rows, 200

    @jwt_required
    def post(self):
        verify_jwt_in_request()
        claims = get_jwt_claims()
        parser = reqparse.RequestParser ()
        # parser.add_argument ('user_id',type=int, help = 'Must be int',location='json',required = True)
        parser.add_argument ('item_id',type=int, help = 'Must be int',location='json',required = True)
        parser.add_argument ('date_order',type=str, help = 'Must be str',location='json',required = True)
        parser.add_argument ('time_order',type=str, help = 'Must be str',location='json',required = True)
        parser.add_argument ('quota_left', type=int, help = 'Must be int',location='json',required = True)
        args =  parser.parse_args ()
        insert = Orders(user_id = claims['user_id'], item_id = args['item_id'], date_order = args['date_order'], time_order = args['time_order'], quota_left = args['quota_left'])
        db.session.add(insert)
        db.session.commit()
        return marshal(insert, order_field), 201
        

    def put(self, id):
        parser = reqparse.RequestParser ()
        parser.add_argument ('user_id',type=int, help = 'Must be int',location='json',required = True)
        parser.add_argument ('item_id',type=int, help = 'Must be int',location='json',required = True)
        parser.add_argument ('date_order',type=str, help = 'Must be str',location='json',required = True)
        parser.add_argument ('time_order',type=str, help = 'Must be str',location='json',required = True)
        parser.add_argument ('quota_left', type=int, help = 'Must be int',location='json',required = True)
        args =  parser.parse_args ()
        
        Orders.query.filter_by(order_id = id).update(dict(
            user_id=args['user_id'],
            item_id=args['item_id'],
            date_order=args['date_order'],
            time_order=args['time_order'],
            quota_left=args['quota_left']
            ))
        db.session.commit()

        #Get Data
        qry = Orders.query.filter_by(order_id=id)
        rows = []
        for row in qry.all():
            rows.append(marshal(row, order_field))
        if rows :
            return rows, 200
        else :
            return {'message' : 'NOT_FOUND'}, 404

    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, required=True, help="ID Order Kosong!",location='args')
        args = parser.parse_args()
        qry = Orders.query.filter_by(order_id = args['id'])
        rows = []
        for row in qry.all():
            rows.append(marshal(row, order_field))
        if rows :
            Orders.query.filter_by(order_id=args['id']).delete()
            db.session.commit()
            return rows, 200
        else :
            return {'message' : 'NOT_FOUND'}, 404

class LoginResource(Resource) :
    def post(self) :
        parser = reqparse.RequestParser()
        parser.add_argument('user_key', type=str, required=True, help="User Key Kosong!", location='json')
        parser.add_argument('user_secret', type=str, required=True, help="User Secret Kosong!", location='json')
        args = parser.parse_args()
        
        qry = Users.query.filter_by(user_key=args['user_key'], user_secret=args['user_secret']).first()
        if qry is None :
            return {'message' : 'Invalid Response 404 status'}, 404
        else :
            token =  create_access_token(identity=qry.user_id)
            return {'token' : token}, 200

############# YUSQI END #####################

############# BAYU START ####################

themoviedb_host = 'https://api.themoviedb.org'
themoviedb_apikey = '2c75a1df7a1409aa228adb5b125d11e4'

class MoviesNowPlaying(Resource):

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('language', type=str, location='args', default='id-ID', choices=('id-ID', 'en-US'))
        args = parser.parse_args()

        rq = requests.get(themoviedb_host + '/3/movie/now_playing', params={'api_key' : themoviedb_apikey, 'language' : args['language']})

        mov = rq.json()
        res = mov['results']
        return res
    
    def post(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('language', type=str, location='args', default='id-ID', choices=('id-ID', 'en-US'))
        args = parser.parse_args()

        rq = requests.get(themoviedb_host + '/3/movie/%s' % (id), params={'api_key' : themoviedb_apikey, 'language' : args['language']})

        mov = rq.json()
        return mov


#################### BAYU END #####################

#################### HABIB START #####################

########### HABIB END #####################

############# ADD RESOURCE ###############
api.add_resource(LoginResource, '/login')
api.add_resource(MeResource, '/me')
api.add_resource(UserResource, '/user', '/user/<int:id>')
api.add_resource(ItemResource, '/item', '/item/<int:id>')
api.add_resource(OrderResource, '/order', '/order/<int:id>')
############# END RESOURCE ################

#Get Client ID
@jwt.user_claims_loader
def add_claims(identity) :
    qry=Users.query.filter_by(user_id=identity).first()
    result=qry.type
    result2=qry.user_id
    return {
        'user_id' : result2,
        'type' : result
    }

if __name__ == '__main__' :
    try :
        if sys.argv[1] == 'db' :
            manager.run()
    except :
        app.run(debug=True, host='127.0.0.1', port=5000)