from db import (
    create_ad,
    get_active_ads,
    get_user_ads,
    get_ad,
    delete_ad,
    increase_progress,
    complete_ad,
    has_completed,
    add_earned,
    create_verification_code,
    verify_code,
    close_ad,
)


class AdsManager:

    REWARD = 0.5
    MIN_TARGET = 10

    @staticmethod
    def create_campaign(
        user_id: int,
        link: str,
        ad_type: str,
        target: int
    ):

        if ad_type not in ("channel", "bot"):
            return {
                "success": False,
                "message": "Invalid advertisement type."
            }

        if target < AdsManager.MIN_TARGET:
            return {
                "success": False,
                "message": f"Minimum target is {AdsManager.MIN_TARGET}."
            }

        return create_ad(
            user_id=user_id,
            link=link,
            ad_type=ad_type,
            target_count=target
        )

    @staticmethod
    def active_channels():

        return get_active_ads("channel")

    @staticmethod
    def active_bots():

        return get_active_ads("bot")

    @staticmethod
    def my_ads(user_id):

        return get_user_ads(user_id)

    @staticmethod
    def get_campaign(ad_id):

        return get_ad(ad_id)

    @staticmethod
    def remove_campaign(ad_id):

        delete_ad(ad_id)

    @staticmethod
    def complete_campaign(user_id: int, ad_id: int):

        # Already completed?
        if has_completed(user_id, ad_id):
            return {
                "success": False,
                "message": "You have already completed this task."
            }

        campaign = get_ad(ad_id)

        if campaign is None:
            return {
                "success": False,
                "message": "Campaign not found."
            }

        if not campaign[9]:
            return {
                "success": False,
                "message": "Campaign is no longer active."
            }

        reward = campaign[6]

        # Save completed task
        complete_ad(user_id, ad_id)

        # Pay reward
        add_earned(user_id, reward)

        # Increase campaign progress
        increase_progress(ad_id)

        return {
            "success": True,
            "reward": reward,
            "message": f"{reward} Birr has been added to your balance."
        }


    @staticmethod
    def verify_task(user_id: int, code: str):

        data = verify_code(code)

        if data is None:
            return {
                "success": False,
                "message": "Invalid or expired verification code."
            }

        if data["user_id"] != user_id:
            return {
                "success": False,
                "message": "This verification code does not belong to you."
            }

        return AdsManager.complete_campaign(
            user_id=user_id,
            ad_id=data["ad_id"]
        )


    @staticmethod
    def finish_campaign(ad_id: int):

        close_ad(ad_id)

        return {
            "success": True,
            "message": "Campaign completed successfully."
        }


    @staticmethod
    def campaign_progress(ad_id: int):

        campaign = get_ad(ad_id)

        if campaign is None:
            return None

        return {
            "current": campaign[5],
            "target": campaign[4],
            "remaining": campaign[4] - campaign[5],
            "status": campaign[8]
        }


    @staticmethod
    def reward_per_user():

        return AdsManager.REWARD


    @staticmethod
    def minimum_target():

        return AdsManager.MIN_TARGET

        return {
            "success": True
        }

    @staticmethod
    def generate_code(
        user_id,
        ad_id
    ):

        return create_verification_code(
            user_id,
            ad_id
        )

    @staticmethod
    def verify(code):

        return verify_code(code)
    @staticmethod
    def get_statistics():

        channels = len(get_active_ads("channel"))
        bots = len(get_active_ads("bot"))

        return {
            "active_channels": channels,
            "active_bots": bots,
            "total_active": channels + bots
        }


    @staticmethod
    def my_statistics(user_id: int):

        campaigns = get_user_ads(user_id)

        total = len(campaigns)
        active = 0
        completed = 0
        closed = 0

        for campaign in campaigns:

            status = campaign[5]

            if status == "active":
                active += 1

            elif status == "completed":
                completed += 1

            elif status == "closed":
                closed += 1

        return {
            "total": total,
            "active": active,
            "completed": completed,
            "closed": closed
        }


    @staticmethod
    def campaign_info(ad_id: int):

        campaign = get_ad(ad_id)

        if campaign is None:
            return None

        return {
            "id": campaign[0],
            "owner": campaign[1],
            "link": campaign[2],
            "type": campaign[3],
            "target": campaign[4],
            "current": campaign[5],
            "reward": campaign[6],
            "total_price": campaign[7],
            "status": campaign[8],
            "is_active": campaign[9],
            "created_at": campaign[10],
            "completed_at": campaign[11]
        }


    @staticmethod
    def active_campaigns():

        channels = get_active_ads("channel")
        bots = get_active_ads("bot")

        return channels + bots


    @staticmethod
    def delete_campaign(ad_id: int):

        campaign = get_ad(ad_id)

        if campaign is None:
            return {
                "success": False,
                "message": "Campaign not found."
            }

        delete_ad(ad_id)

        return {
            "success": True,
            "message": "Campaign deleted successfully."
        }


    @staticmethod
    def admin_close(ad_id: int):

        campaign = get_ad(ad_id)

        if campaign is None:
            return {
                "success": False,
                "message": "Campaign not found."
            }

        close_ad(ad_id)

        return {
            "success": True,
            "message": "Campaign closed successfully."
        }


    @staticmethod
    def campaign_exists(ad_id: int):

        return get_ad(ad_id) is not None