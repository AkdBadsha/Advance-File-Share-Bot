#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) @AlbertEinsteinTG

import motor.motor_asyncio


class JoinReqs:

    def __init__(self):
        from info import JOIN_REQS_DB

        if JOIN_REQS_DB:
            self.client = motor.motor_asyncio.AsyncIOMotorClient(JOIN_REQS_DB)
            self.db = self.client["JoinReqs"]
            self.col = self.db["join_reqs"]
        else:
            self.client = None
            self.db = None
            self.col = None

    def isActive(self):
        if self.client is not None:
            return True
        else:
            return False

    async def add_user(self, user_id, first_name, username, date, channel_id):
        try:
            await self.col.insert_one(
                {
                    "_id": int(user_id),
                    "user_id": int(user_id),
                    "first_name": first_name,
                    "username": username,
                    "date": date,
                    "channel_id": channel_id,
                }
            )
        except:
            pass

    async def get_user(self, user_id):
        return await self.col.find_one({"user_id": int(user_id)})

    async def is_user_joined_all(self, user_id, channel_ids: list):
        # Get count of docs matching user_id and each channel_id
        count = await self.col.count_documents(
            {"user_id": int(user_id), "channel_id": {"$in": channel_ids}}
        )
        # Return True only if docs exist for all channel_ids
        return count == len(channel_ids)

    async def get_all_users(self):
        return await self.col.find().to_list(None)

    async def delete_user(self, user_id):
        await self.col.delete_one({"user_id": int(user_id)})

    async def delete_all_users(self):
        await self.col.delete_many({})

    async def get_all_users_count(self):
        return await self.col.count_documents({})
