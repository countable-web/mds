import uuid
from datetime import datetime
from flask_restplus import Resource, reqparse
from ..models.mines import MineIdentity
from ..models.person import Person, MgrAppointment

from app.extensions import jwt


class PersonResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('first_name', type=str)
    parser.add_argument('surname', type=str)

    @jwt.requires_roles(["mds-mine-view"])
    def get(self, person_guid):
        person = Person.find_by_person_guid(person_guid)
        if person:
            return person.json()
        return {'message': 'Person not found'}, 404

    @jwt.requires_roles(["mds-mine-create"])
    def post(self, person_guid=None):
        if person_guid:
            return {'error': 'Unexpected person id in Url.'}, 400
        data = PersonResource.parser.parse_args()
        if not data['first_name']:
            return {'error': 'Must specify a first name.'}, 400
        if not data['surname']:
            return {'error': 'Must specify a surname.'}, 400
        person_exists=Person.find_by_name(data['first_name'], data['surname'])
        if person_exists:
            return {'error': 'Person with the name: {} {} already exists'.format(data['first_name'], data['surname'])}
        # Dummy User for now
        dummy_user_kwargs = { 'create_user': 'DummyUser', 'update_user': 'DummyUser' }
        person=Person(person_guid=uuid.uuid4(),
            first_name=data['first_name'],
            surname=data['surname'],
            **dummy_user_kwargs
            )
        person.save()
        return { 'person_guid': str(person.person_guid), 'first_name': person.first_name, 'surname': person.surname }

    @jwt.requires_roles(["mds-mine-create"])
    def put(self, person_guid):
        data = PersonResource.parser.parse_args()
        person_exists = Person.find_by_person_guid(person_guid)
        if not person_exists:
            return {'message': 'Person not found'}, 404

        first_name = data['first_name'] if data['first_name'] else person_exists.first_name
        surname = data['surname'] if data['surname'] else person_exists.surname
        person_name_exists=Person.find_by_name(first_name, surname)
        if person_name_exists:
            return {'error': 'Person with the name: {} {} already exists'.format(first_name, surname)}
        person_exists.first_name=first_name
        person_exists.surname=surname
        person_exists.save()
        return person_exists.json()


class ManagerResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('person_guid', type=str)
    parser.add_argument('mine_guid', type=str)
    parser.add_argument('effective_date', type=lambda x: datetime.strptime(x,'%Y-%m-%d'))
    parser.add_argument('expiry_date', type=lambda x: datetime.strptime(x,'%Y-%m-%d'))

    @jwt.requires_roles(["mds-mine-view"])
    def get(self, mgr_appointment_guid):
        manager = MgrAppointment.find_by_mgr_appointment_guid(mgr_appointment_guid)
        if manager:
            return manager.json()
        return {'message': 'Manager not found'}, 404

    @jwt.requires_roles(["mds-mine-create"])
    def post(self, mgr_appointment_guid=None):
        if mgr_appointment_guid:
            return {'error': 'Unexpected manager id in Url.'}, 400
        data = ManagerResource.parser.parse_args()
        if not data['person_guid']:
            return {'error': 'Must specify a person guid.'}, 400
        if not data['mine_guid']:
            return {'error': 'Must specify a mine guid.'}, 400
        if not data['effective_date']:
            return {'error': 'Must specify a effective_date.'}, 400
        if not data['expiry_date']:
            return {'error': 'Must specify a expiry_date.'}, 400
        # Validation for mine and person exists
        person_exists = Person.find_by_person_guid(data['person_guid'])
        if not person_exists:
            return {'error': 'Person with guid: {}, does not exist.'.format(data['person_guid'])}
        mine_exists = MineIdentity.find_by_mine_guid(data['mine_guid'])
        if not mine_exists:
            return {'error': 'Mine with guid: {}, does not exist.'.format(data['mine_guid'])}
        # Dummy User for now
        dummy_user_kwargs = { 'create_user': 'DummyUser', 'update_user': 'DummyUser' }
        manager=MgrAppointment(
            mgr_appointment_guid=uuid.uuid4(), 
            person_guid=data['person_guid'], 
            mine_guid=data['mine_guid'], 
            effective_date=data['effective_date'],
            expiry_date=data['expiry_date'],
            **dummy_user_kwargs
            )
        manager.save()
        return { 'person_guid': str(manager.person_guid), 'mgr_appointment_guid': str(manager.mgr_appointment_guid), 'mine_guid': str(manager.mine_guid) }


class PersonList(Resource):
    @jwt.requires_roles(["mds-mine-view"])
    def get(self):
        return { 'persons': list(map(lambda x: x.json(), Person.query.all())) }