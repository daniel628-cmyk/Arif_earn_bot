from db import (
    get_db,
    get_balance,
    add_earned,
    remove_deposit,
    has_completed,
    complete_ad,
    increase_progress,
    create_verification_code,
    verify_code,
    close_ad,
)

REWARD = 0.27


class AdsManager:

    @staticmethod
    def create_campaign(
        user_id: int,
        link: str,
        ad_type: str,
        target: int,
    ):

        total_price = round(target * REWARD, 2)

        balance = get_balance(user_id)

        if balance["deposit"] < total_price:
            return {
                "success": False,
                "message": "Insufficient deposit balance."
            }

        remove_deposit(
            user_id,
            total_price
        )

        conn = get_db()

        try:

            with conn.cursor() as cur:

                cur.execute(
                    """
                    INSERT INTO ads
                    (
                        user_id,
                        link,
                        type,
                        target_count,
                        current_count,
                        reward,
                        total_price,
                        status,
                        is_active
                    )
                    VALUES
                    (
                        %s,
                        %s,
                        %s,
                        %s,
                        0,
                        %s,
                        %s,
                        'active',
                        TRUE
                    )
                    RETURNING id
                    """,
                    (
                        user_id,
                        link,
                        ad_type,
                        target,
                        REWARD,
                        total_price,
                    ),
                )

                ad_id = cur.fetchone()[0]

            conn.commit()

            return {
                "success": True,
                "ad_id": ad_id,
                "total_price": total_price,
            }

        except Exception as e:

            conn.rollback()

            return {
                "success": False,
                "message": str(e),
            }

        finally:

            conn.close()
    @staticmethod
    def active_channels():

        conn = get_db()

        try:

            with conn.cursor() as cur:

                cur.execute("""
                    SELECT
                        id,
                        user_id,
                        link,
                        target_count,
                        current_count,
                        reward
                    FROM ads
                    WHERE
                        type='channel'
                        AND is_active=TRUE
                        AND status='active'
                    ORDER BY id ASC
                """)

                return cur.fetchall()

        finally:

            conn.close()


    @staticmethod
    def active_bots():

        conn = get_db()

        try:

            with conn.cursor() as cur:

                cur.execute("""
                    SELECT
                        id,
                        user_id,
                        link,
                        target_count,
                        current_count,
                        reward
                    FROM ads
                    WHERE
                        type='bot'
                        AND is_active=TRUE
                        AND status='active'
                    ORDER BY id ASC
                """)

                return cur.fetchall()

        finally:

            conn.close()


    @staticmethod
    def my_ads(user_id):

        conn = get_db()

        try:

            with conn.cursor() as cur:

                cur.execute("""
                    SELECT
                        id,
                        link,
                        type,
                        target_count,
                        current_count,
                        status,
                        reward,
                        total_price,
                        created_at
                    FROM ads
                    WHERE user_id=%s
                    ORDER BY id DESC
                """, (user_id,))

                return cur.fetchall()

        finally:

            conn.close()


    @staticmethod
    def campaign_info(ad_id):

        conn = get_db()

        try:

            with conn.cursor() as cur:

                cur.execute("""
                    SELECT
                        id,
                        user_id,
                        link,
                        type,
                        target_count,
                        current_count,
                        reward,
                        total_price,
                        status,
                        is_active,
                        created_at
                    FROM ads
                    WHERE id=%s
                """, (ad_id,))

                row = cur.fetchone()

                if row is None:
                    return None

                return {
                    "id": row[0],
                    "owner": row[1],
                    "link": row[2],
                    "type": row[3],
                    "target": row[4],
                    "current": row[5],
                    "reward": row[6],
                    "total_price": row[7],
                    "status": row[8],
                    "is_active": row[9],
                    "created_at": row[10],
                }

        finally:

            conn.close()
    @staticmethod
    def delete_campaign(ad_id):

        conn = get_db()

        try:

            with conn.cursor() as cur:

                cur.execute(
                    "DELETE FROM ads WHERE id=%s",
                    (ad_id,)
                )

            conn.commit()

            return True

        finally:

            conn.close()


    @staticmethod
    def finish_campaign(ad_id):

        close_ad(ad_id)

        return True


    @staticmethod
    def generate_code(
        user_id: int,
        ad_id: int
    ):

        return create_verification_code(
            user_id=user_id,
            ad_id=ad_id
        )


    @staticmethod
    def verify(code: str):

        return verify_code(code)
    @staticmethod
    def complete_campaign(
        user_id: int,
        ad_id: int
    ):

        # Already completed?
        if has_completed(user_id, ad_id):
            return {
                "success": False,
                "message": "You already completed this advertisement."
            }

        # Campaign info
        info = AdsManager.campaign_info(ad_id)

        if info is None:
            return {
                "success": False,
                "message": "Advertisement not found."
            }

        if not info["is_active"]:
            return {
                "success": False,
                "message": "Advertisement is already closed."
            }

        reward = info["reward"]

        # Save completed task
        complete_ad(
            user_id=user_id,
            ad_id=ad_id
        )

        # Add reward
        add_earned(
            user_id=user_id,
            amount=reward
        )

        # Increase campaign progress
        increase_progress(ad_id)

        # Reload campaign info
        info = AdsManager.campaign_info(ad_id)

        completed = False

        if info["current"] >= info["target"]:

            AdsManager.finish_campaign(ad_id)

            completed = True

        return {
            "success": True,
            "reward": reward,
            "completed": completed,
            "current": info["current"],
            "target": info["target"],
            "message": f"{reward:.2f} Birr added successfully."
        }
    @staticmethod
    def total_active():

        return (
            len(AdsManager.active_channels()) +
            len(AdsManager.active_bots())
        )


    @staticmethod
    def campaign_exists(ad_id):

        return AdsManager.campaign_info(ad_id) is not None


    @staticmethod
    def total_channels():

        return len(
            AdsManager.active_channels()
        )


    @staticmethod
    def total_bots():

        return len(
            AdsManager.active_bots()
        )


    @staticmethod
    def campaign_progress(ad_id):

        info = AdsManager.campaign_info(ad_id)

        if info is None:
            return None

        return {
            "current": info["current"],
            "target": info["target"],
            "remaining": max(
                0,
                info["target"] - info["current"]
            ),
            "completed": info["current"] >= info["target"]
        }


    @staticmethod
    def reward_amount():

        return REWARD