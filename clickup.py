#!/usr/bin/python3
# -*- coding: utf-8 -*-

# ClickUp API doc: https://clickup.com/api

import asyncio
import json
import platform
import os
import time
from urllib.request import Request, urlopen
from aiohttp import ClientSession
from typing import (
    Any,
    Coroutine,
    Dict,
    Optional
)


class Task(object):
    def __init__(self, space: str, folder: str, list: str, name: str, description: str, fields: str = ''):
        self.meta = {
            'space': space,
            'folder': folder,
            'list': list
        }
        self.name = name
        self.description = description
        self.assignees = []
        self.tags = []
        self.status = "to do"
        self.priority = None
        self.due_date = None
        self.due_date_time = False
        self.time_estimate = None
        self.start_date = int(time.time()*1000)
        self.start_date_time = False
        self.notify_all = True
        self.parent = None
        self.links_to = None
        self.check_required_custom_fields = False
        self.custom_fields = [
            # {
            #     "id": "0a52c486-5f05-403b-b4fd-c512ff05131c",
            #     "value": 23
            # },
            # {
            #     "id": "03efda77-c7a0-42d3-8afd-fd546353c2f5",
            #     "value": "Text field input"
            # }
        ]
        # self.parse_fields(fields)

    def parse_fields(self, fields: str):
        if fields == '':
            self.fields = {}
        else:
            self.fields = {
                'fields': fields
            }


class ClickUpAPIEndpoint(object):
    def __init__(self) -> None:
        self.task = {
            'create': 'https://api.clickup.com/api/v2/list/{list}/task'
        }
        self.list = {
            'get_all': 'https://api.clickup.com/api/v2/folder/{folder}/list?archived=false'
        }
        self.folderless_list = {
            'get_all': 'https://api.clickup.com/api/v2/space/{space}/list?archived=false'
        }
        self.folder = {
            'get_all': 'https://api.clickup.com/api/v2/space/{space}/folder?archived=false'
        }
        self.space = {
            'get_all': 'https://api.clickup.com/api/v2/team/{team}/space?archived=false'
        }
        self.team = {
            'get_all': 'https://api.clickup.com/api/v2/team'
        }


class Client(object):
    def __init__(self, token: str):
        self.api = ClickUpAPIEndpoint()
        self.default_team = None
        self.header = {
            'Authorization': token,
            'Content-Type': 'application/json'
        }

    async def test_connection(self) -> Coroutine[Any, Any, str]:
        api_endpoint = 'https://api.clickup.com/api/v2/team'
        async with ClientSession() as session:
            response = await session.request('GET', api_endpoint, headers=self.header)
            response.raise_for_status()
            return response.text()

    async def make_request(self, session: ClientSession, method: str, api_endpoint: str, body: Optional[Dict[str, Any]] = None, url_params: Optional[Dict[str, Any]] = None):
        if url_params is not None:
            api_endpoint = api_endpoint.format(**url_params)
        response = await session.request(method, api_endpoint, data=body, headers=self.header)
        response.raise_for_status()
        content = await response.text()
        return json.loads(content), response.status

    async def get_team(self, session, name: str):
        jobj, status = await self.make_request(
            session, 'GET', self.api.team['get_all'])
        try:
            match = [x for x in jobj['teams']
                     if name.lower() == x['name'].lower()]
            if len(match) == 0:
                match = [x for x in jobj['teams']
                         if x['name'].lower().startswith(name.lower())]
            return match[0]
        except IndexError:
            print('workspace "{}" not found in response.')

    async def get_space(self, session: ClientSession, team_id: str, name: str):
        jobj, status = await self.make_request(
            session, 'GET', self.api.space['get_all'], url_params={'team': team_id})
        try:
            match = [x for x in jobj['spaces']
                     if name.lower() == x['name'].lower()]
            if len(match) == 0:
                match = [x for x in jobj['spaces']
                         if x['name'].lower().startswith(name.lower())]
            return match[0]
        except IndexError:
            print('space "{}" not found in response.')

    async def get_folder(self, session: ClientSession, space_id: str, name: str):
        jobj, status = await self.make_request(
            session, 'GET', self.api.folder['get_all'], url_params={'space': space_id})
        try:
            match = [x for x in jobj['folders']
                     if name.lower() == x['name'].lower()]
            if len(match) == 0:
                match = [x for x in jobj['folders']
                         if x['name'].lower().startswith(name.lower())]
            return match[0]
        except IndexError:
            print('folder "{}" not found in response.')

    async def get_folderless_list(self, session: ClientSession, space_id: str, name: str):
        jobj, status = await self.make_request(
            session, 'GET', self.api.folderless_list['get_all'], url_params={'space': space_id})
        try:
            match = [x for x in jobj['lists']
                     if name.lower() == x['name'].lower()]
            if len(match) == 0:
                match = [x for x in jobj['lists']
                         if x['name'].lower().startswith(name.lower())]
            return match[0]
        except IndexError:
            print('list "{}" not found in response.')

    async def get_list(self, session: ClientSession, folder_id: str, name: str):
        jobj, status = await self.make_request(
            session, 'GET', self.api.list['get_all'], url_params={'folder': folder_id})
        try:
            match = [x for x in jobj['lists']
                     if name.lower() == x['name'].lower()]
            if len(match) == 0:
                match = [x for x in jobj['lists']
                         if x['name'].lower().startswith(name.lower())]
            return match[0]
        except IndexError:
            print('list "{}" not found in response.')

    async def post_task(self, session: ClientSession, list_id: str, task: Task):
        data = task.__dict__
        data.pop('meta')
        data = json.dumps(data)
        jobj, status = await self.make_request(
            session, 'POST', self.api.task['create'], data, {'list': list_id})
        return jobj

    async def create_task(self, task: Task):
        async with ClientSession() as session:
            team = await self.get_team(session, 'Simbio IT')
            space = await self.get_space(session, team['id'], task.meta['space'])
            if task.meta['folder'] == '':
                list_ = await self.get_folderless_list(session, space['id'], task.meta['list'])
            else:
                folder = await self.get_folder(session, space['id'], task.meta['folder'])
                list_ = await self.get_list(session, folder['id'], task.meta['list'])
            task = await self.post_task(session, list_['id'], task)
            return task


def main():
    client = Client(os.getenv('CLICKUP_TOKEN'))
    # BUG: asyncio needs special configuration on Windows
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    response = asyncio.run(client.test_connection())
    print(response)
    task = Task('simbio', '', 't', 'title', 'description')
    response = asyncio.run(client.create_task(task))
    print(response)


if __name__ == '__main__':
    main()
