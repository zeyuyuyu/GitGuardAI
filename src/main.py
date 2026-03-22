# src/main.py
import asyncio
import random

class GovernanceProtocol:
    def __init__(self, agents):
        self.agents = agents
        self.proposal_queue = []
        self.vote_results = {}

    async def propose_action(self, agent, action):
        self.proposal_queue.append((agent, action))
        await self.initiate_vote()

    async def initiate_vote(self):
        if len(self.proposal_queue) > 0:
            proposal = self.proposal_queue.pop(0)
            agent, action = proposal
            self.vote_results = {agent: 0 for agent in self.agents}
            await asyncio.gather(*[self.agent_vote(a, action) for a in self.agents])
            if sum(self.vote_results.values()) >= len(self.agents) // 2 + 1:
                print(f"Proposal accepted: {agent} wants to {action}")
                await agent.execute_action(action)
            else:
                print(f"Proposal rejected: {agent} wanted to {action}")

    async def agent_vote(self, agent, action):
        vote = random.choice([True, False])
        self.vote_results[agent] = 1 if vote else 0
        print(f"{agent.name} voted {'yes' if vote else 'no'} on {action}")

class Agent:
    def __init__(self, name):
        self.name = name

    async def execute_action(self, action):
        print(f"{self.name} executing action: {action}")

async def main():
    agents = [Agent(f"Agent{i}") for i in range(5)]
    protocol = GovernanceProtocol(agents)

    await asyncio.gather(
        *[protocol.propose_action(random.choice(agents), "move left"),
          protocol.propose_action(random.choice(agents), "move right"),
          protocol.propose_action(random.choice(agents), "attack")]
    )

asyncio.run(main())