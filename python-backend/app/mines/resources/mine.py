import uuid

from app.db import db
from flask_restplus import Resource, reqparse
from ..models.mines import MineIdentity, MineDetail, MineralTenureXref
from ..utils.random import generate_mine_no


class Mine(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str)
    parser.add_argument('tenure_number_id', type=str)

    def get(self, mine_no):
        mine = MineIdentity.find_by_mine_no(mine_no)
        if mine:
            return mine.json()
        return {'message': 'Mine not found'}, 404

    def post(self, mine_no):
        data = Mine.parser.parse_args()
        if not data['name']:
            return {'error': 'Must specify a name.'}, 400
        if len(data['name']) > 60:
            return {'error': 'Specified name exceeds 60 characters.'}, 400
        # Dummy User for now
        dummy_user = 'DummyUser'
        dummy_user_kwargs = { 'create_user': dummy_user, 'update_user': dummy_user }
        mine_identity= MineIdentity(mine_guid = uuid.uuid4(), **dummy_user_kwargs)
        mine_identity.save()
        mine_detail = MineDetail(mine_guid=mine_identity.mine_guid, mine_no=generate_mine_no(), mine_name=data['name'], **dummy_user_kwargs)
        mine_detail.save()
        return { 'mine_guid': str(mine_detail.mine_guid), 'mine_no': mine_detail.mine_no, 'mine_name': mine_detail.mine_name }

    def put(self, mine_no):
        data = Mine.parser.parse_args()
        if not data['tenure_number_id']:
            return {'error': 'Must specify tenure_id.'}, 400
        mine = MineIdentity.find_by_mine_no(mine_no)
        if not mine:
            return {'message': 'Mine not found'}, 404
        tenure = data['tenure_number_id']
        dummy_user = 'DummyUser'
        dummy_user_kwargs = { 'create_user': dummy_user, 'update_user': dummy_user }
        tenure = MineralTenureXref(mine_guid=mine.mine_guid, tenure_number_id=tenure, **dummy_user_kwargs)
        tenure.save()
        return mine.json()

class MineList(Resource):
    def get(self):
        return { 'mines': list(map(lambda x: x.json(), MineIdentity.query.all())) }
