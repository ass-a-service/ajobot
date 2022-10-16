from disnake import MessageInteraction, Member
from disnake.ui import View

class LeaderboardCustomView(View):
    def __init__(self, member: Member, page: int = 1):
        self.member = member
        self.page = page
        super().__init__(timeout=180)

    async def interaction_check(self, inter: MessageInteraction) -> bool:
        if inter.author != self.member:
            await inter.response.send_message(content="You don't have permission to press this button.", ephemeral=True)
            return False
        return True
