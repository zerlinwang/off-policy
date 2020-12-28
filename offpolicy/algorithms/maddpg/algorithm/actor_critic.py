import torch
import torch.nn as nn
from offpolicy.utils.util import init, to_torch
from offpolicy.algorithms.utils.mlp import MLPBase
from offpolicy.algorithms.utils.act import ACTLayer

class MADDPG_Actor(nn.Module):
    def __init__(self, args, obs_dim, act_dim, device):
        super(MADDPG_Actor, self).__init__()
        self._use_orthogonal = args.use_orthogonal
        self._gain = args.gain
        self.hidden_size = args.hidden_size
        self.device = device
        self.tpdv = dict(dtype=torch.float32, device=device)

        # map observation input into input for rnn
        self.mlp = MLPBase(args, obs_dim)

        # get action from rnn hidden state
        self.act = ACTLayer(act_dim, self.hidden_size, self._use_orthogonal, self._gain)

        self.to(device)

    def forward(self, x):
        # make sure input is a torch tensor
        x = to_torch(x).to(**self.tpdv)

        x = self.mlp(x)
        # pass outputs through linear layer
        action = self.act(x)

        return action


class MADDPG_Critic(nn.Module):
    def __init__(self, args, central_obs_dim, central_act_dim, device, num_q_outs=1):
        super(MADDPG_Critic, self).__init__()
        self._use_orthogonal = args.use_orthogonal
        self.hidden_size = args.hidden_size
        self.device = device
        self.tpdv = dict(dtype=torch.float32, device=device)

        input_dim = central_obs_dim + central_act_dim

        self.mlp = MLPBase(args, input_dim)

        init_method = [nn.init.xavier_uniform_, nn.init.orthogonal_][self._use_orthogonal]
        def init_(m):
            return init(m, init_method, lambda x: nn.init.constant_(x, 0))
        self.q_outs = [init_(nn.Linear(self.hidden_size, 1)) for _ in range(num_q_outs)]
        
        self.to(device)

    def forward(self, central_obs, central_act):
        # ensure inputs are torch tensors
        central_obs = to_torch(central_obs).to(**self.tpdv)
        central_act = to_torch(central_act).to(**self.tpdv)

        x = torch.cat([central_obs, central_act], dim=1)

        x = self.mlp(x)
        q_values = [q_out(x) for q_out in self.q_outs]

        return q_values
