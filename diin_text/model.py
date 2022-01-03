# AUTOGENERATED! DO NOT EDIT! File to edit: notebooks/01_model.ipynb (unless otherwise specified).

__all__ = ['ForwardHook', 'get_linear_layer_activations_states']

# Cell
class ForwardHook():
    def __init__(self, module, name:None, activation:bool, stats:bool):
        ''' Track stats and activations of any layer in model '''
        self.hook = module.register_forward_hook(self.hook_fn)
        self.status = 'active'
        self.name = name
        self.activation_status = activation
        self.stats = stats
        if self.activation_status: self.activations = []
        if stats: self.means, self.stds = [], []

    def hook_fn(self, module, input, output):
        '''This class can be inheritet this class and define your own hook_fn'''
        if self.activation_status: self.activations.append ( output[1].detach().cpu().numpy() )
        if self.stats:
          self.means += output[1].mean(1).detach().cpu().numpy().squeeze().tolist()
          self.stds += output[1].std(1).detach().cpu().numpy().squeeze().tolist()

    def _stack_activations(self):
        '''Stack all output(activations) once all outputs are saved in ForwardHook.activations'''
        self.activations = np.vstack(self.activations)

    def close(self):
        '''remove the hook'''
        self.hook.remove()
        self.status = 'removed'

# Cell
def get_linear_layer_activations_states(dls, model, layers:list, stats:bool, activation:bool, output:bool, remove_hooks=True):
  ''' useful when model is trained and want to analyze intermediate layers'''

  hooks = dict()
  if output: output_list = []

  for layer in layers:
    if hasattr(model, layer): hooks[f'{layer}'] = ForwardHook ( getattr(model, layer),layer, activation=activation, stats=stats )

  model.eval()
  i = 0
  for batch in tqdm(dls, desc='Fatching data: '):
    with torch.no_grad():
        i+=1
        out = model(batch)
        if output: output_list.append( (out) )

  for k,v in hooks.items():
    if activation: v._stack_activations()
    if remove_hooks: v.close()

  if output:
      return hooks, output_list
  else:
      return hooks