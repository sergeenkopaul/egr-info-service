from asyncio import create_task

from aiohttp import ClientSession
from fastapi import HTTPException

from constants import API_URLS_FOR_QUERING_EGR

ENDPOINTS_TO_FIELDS = {
    'getBaseInfoByRegNum' : {
        'vat_number' : ('ngrn',), 
        'reg_date' : ('dfrom',),
        'status' : ('nsi00219', 'vnsostk'),
        'subject_type' : ('nsi00211', 'nkvob'),
    },
    'getAddressByRegNum' : {
        'country' : ('nsi00201', 'vnstranp'),
        'index' : ('nindex',),
        'locality_type' : ('nsi00239', 'vntnpk'),
        'locality' : ('vnp',),
        'type_of_road_network_element' : ('nsi00226', 'vntulk'),
        'name_of_road_network_element' : ('vulitsa',),
        'house_num' : ('vdom',),
        'room_type' : ('nsi00227', 'vntpomk'),
        'room_number' : ('vpom',),
        'email' : ('vemail',),
        'phone_number' : ('vtels',),
        'site' : ('vsite',),
    },
    'getJurNamesByRegNum' : {
        'full_name' : ('vnaim',),
        'short_name' : ('vn',),
    },
    'getVEDByRegNum' : {
        'ved_code' : ('nsi00114', 'vkvdn'),
        'ved_name' : ('nsi00114', 'vnvdnp'),
    },
    'getIPFIOByRegNum' : {
        'sp_name' : ('vfio',),
    },
    'getEventByRegNum' : {
        'event_date' : ('dfrom',),
        'agency' : ('nsi00212', 'vnuzp'),
        'event_name' : ('nsi00223', 'vnop'),
        'docs_receiving_date' : ('ddoc',),
        'event_basis' : ('nsi00213', 'vnosn'),
    },
    'getShortInfoByRegName' : {
        'vat_number_by_name' : ('ngrn',),
    }
}

async def find_vat(vat_number : int):
    data = []
    async with ClientSession(API_URLS_FOR_QUERING_EGR['base']) as session:
        
        task = create_task(make_request(session, vat_number, ['vat_number']))
        vat_number = (await task).get('vat_number')
        if vat_number:
            data.append(vat_number)

    return data

async def find_vat_by_name(name : str):
    data = []
    async with ClientSession(API_URLS_FOR_QUERING_EGR['base']) as session:
        subjects_info = await create_task(make_request(session, name, ['vat_number_by_name']))
        if any([endpoint in subjects_info for endpoint in ENDPOINTS_TO_FIELDS]):
            data = [int(info['vat_number_by_name']) for info in list(subjects_info.values())[0]]
        elif subjects_info.get('vat_number_by_name', None):
            data = [int(subjects_info['vat_number_by_name'])]

    return data

async def get_full_info_about_subject(vat_number : int):
    data = {}
    async with ClientSession(API_URLS_FOR_QUERING_EGR['base']) as session:
        task = create_task(make_request(session, vat_number, ['__all__']))
        data = await task

    return data

async def get_base_info_about_subject(vat_number : int):
    data = {}
    async with ClientSession(API_URLS_FOR_QUERING_EGR['base']) as session:
        subject_type = await create_task(make_request(session, vat_number, ['subject_type']))
        if subject_type['subject_type'] == 1:
            fields = [
                'short_name', 'name', 'vat_number', 'status', 'country', 'index', 'locality_type', 'locality',
                'type_of_road_network_element', 'name_of_road_network_element', 'house_num', 'room_type', 
                'room_number', 'email', 'phone_number', 'ved_name'
            ]
        elif subject_type['subject_type'] == 2:
            fields = ['sp_name', 'vat_number', 'status', 'ved_name']

        data = await create_task(make_request(session, vat_number, fields))

    return data | subject_type

def get_data_from_api_decorator(func):
    async def wrapper(*args, **kwargs):
        def unpack(args, kwargs) -> tuple:
            if len(args) + len(kwargs) != len(args) and len(args) + len(kwargs) != len(kwargs):
                raise Exception({'message' : 'Specify either args or kwargs in query.'})
            elif args:
                session = args[0]
                value_for_search = args[1]
                fields = args[2]
            elif kwargs:
                session = kwargs['session']
                value_for_search = kwargs['value_for_search']
                fields = kwargs['fields']
            return session, value_for_search, fields
        
        def prepare_fields(fields):
            if fields[0] == '__all__':
                fields = []
                fields_from_endpoints = ENDPOINTS_TO_FIELDS.values()
                for fields_set in fields_from_endpoints:
                    fields.extend(list(fields_set.keys()))
            return fields
        
        def prepare_endpoint_to_fields(fields):
            result = {}
            for endpoint in ENDPOINTS_TO_FIELDS:
                fields_list = []
                for field in fields:
                    if field in ENDPOINTS_TO_FIELDS[endpoint]:
                        fields_list.append(field)

                if fields_list: 
                    result[endpoint] = fields_list

            return result

        result = {}
        session, value_for_search, fields = unpack(args, kwargs)
        fields = prepare_fields(fields)
        endpoint_to_fields = prepare_endpoint_to_fields(fields)
        for endpoint in endpoint_to_fields:
            async with session.get(f'{API_URLS_FOR_QUERING_EGR['external']}/{endpoint}/{value_for_search}', ssl=False) as response:
                if response.status >= 500:
                    raise HTTPException(503, "Information cannot be provided due to unavailability of the service https://egr.gov.by/api/swagger-ui.html#/main-controller.")
                elif response.status == 200:
                    data = await response.json()
                    data = data[0] if isinstance(data, list) and len(data) == 1 else data
                    result = result | await func(session, value_for_search, endpoint_to_fields[endpoint], data=data, endpoint=endpoint)

        return result
        
    return wrapper

@get_data_from_api_decorator
async def make_request(session : ClientSession, value_for_search : int | str, fields : list[str], data : dict | list[dict], endpoint : str):
    async def extract_data(chunk : dict, fields : list[str]) -> dict:
        result = {}
        for field in fields:
            data_path_parts = ENDPOINTS_TO_FIELDS[endpoint][field]
            data = chunk.get(data_path_parts[0], {})
            for path_part in data_path_parts[1:]:
                data = data.get(path_part, {})

            result[field] = data

        return result
    
    result = {}
    if isinstance(data, list):
        tasks = [create_task(extract_data(chunk, fields)) for chunk in data]
        result = {endpoint : [await task for task in tasks]}
    elif isinstance(data, dict):
        result = await create_task(extract_data(data, fields))
    else:
        'raise excep'
    return result