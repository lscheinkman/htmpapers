# ----------------------------------------------------------------------
# Numenta Platform for Intelligent Computing (NuPIC)
# Copyright (C) 2019, Numenta, Inc.  Unless you have an agreement
# with Numenta, Inc., for a separate license for this software code, the
# following terms and conditions apply:
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Affero Public License for more details.
#
# You should have received a copy of the GNU Affero Public License
# along with this program.  If not, see http://www.gnu.org/licenses.
#
# http://numenta.org/licenses/
# ----------------------------------------------------------------------
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

import logging
import multiprocessing
import os

from pytorch.audio_transforms import *
from pytorch.benchmark_utils import (
  register_nonzero_counter, unregister_counter_nonzero)
from pytorch.model_utils import evaluateModel
from pytorch.speech_commands_dataset import SpeechCommandsDataset
from torch.utils.data import DataLoader
from torchvision import transforms
from tqdm import tqdm

logging.basicConfig(level=logging.ERROR)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from tabulate import tabulate

import pandas as pd
from pytorch.sparse_speech_experiment import SparseSpeechExperiment



def analyzeWeightPruning(args):
  """
  Multiprocess function used to analyze the impact of nonzeros and accuracy
  after pruning low weights and units with low dutycycle of a pre-trained model.

  :param args:  tuple with the following arguments:
                - experiment path: The experiment results path
                - configuration parameters: The parameters used in the experiment run
                - minWeight: min weight to prune. If zero then no pruning
                - minDutycycle: min threshold to prune. If less than zero then no pruning
                - progress bar position:
                When 'minWeight' is zero
  :type args:   tuple

  :return: Panda DataFrame with the nonzero count for every weight variable in
           the model and the evaluation results after the pruning the weights.
  :rtype: :class:`pandas.DataFrame`
  """
  path, params, minWeight, minDutycycle, position = args

  device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

  datadir = os.path.join(params["datadir"], "speech_commands")
  testDataDir = os.path.join(datadir, "test")

  # Initialize speech test dataset for this experiment
  n_mels = 32
  testFeatureTransform = transforms.Compose([
    FixAudioLength(),
    ToMelSpectrogram(n_mels=n_mels),
    ToTensor('mel_spectrogram', 'input'),
    Unsqueeze(tensor_name="input", model_type=params["model_type"])
  ])
  testDataset = SpeechCommandsDataset(
    testDataDir,
    testFeatureTransform,
    silence_percentage=0,
  )

  test_loader = DataLoader(testDataset,
                           batch_size=params["batch_size"],
                           sampler=None,
                           shuffle=False
                           )

  # Load pre-trained model and evaluate with test dataset
  model = torch.load(os.path.join(path, "model.pt"), map_location=device)

  label = str(minWeight)
  name = params["name"]
  desc = "{}.minW({}).minD({})".format(name, minWeight, minDutycycle)

  model.pruneWeights(minWeight)
  model.pruneDutycycles(minDutycycle)

  # Collect nonzero
  nonzero = {}
  register_nonzero_counter(model, nonzero)
  results = evaluateModel(model=model, loader=test_loader, device=device,
                          progress={"desc": desc, "position": position})
  unregister_counter_nonzero(model)

  # Create table with results
  table = pd.DataFrame.from_dict(nonzero)
  noise_score = results["total_correct"]
  table = table.assign(accuracy=results["accuracy"])

  # Compute noise score
  noise_values = tqdm([0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5],
                      position=position)
  # Create noise dataset with noise transform
  noiseTransform = transforms.Compose([
    FixAudioLength(),
    ToSTFT(),
    ToMelSpectrogramFromSTFT(n_mels=n_mels),
    DeleteSTFT(),
    ToTensor('mel_spectrogram', 'input'),
    Unsqueeze(tensor_name="input", model_type=params["model_type"])
  ])

  noiseDataset = SpeechCommandsDataset(
    testDataDir,
    noiseTransform,
    silence_percentage=0,
  )
  noise_loader = DataLoader(noiseDataset,
                            batch_size=params["batch_size"],
                            sampler=None,
                            shuffle=False
                            )

  for noise in noise_values:
    noise_values.set_description("{}.noise({})".format(desc, noise))

    xfrom = AddNoise(noise)
    # Add noise to dataset transforms
    noiseTransform.transforms.insert(1, xfrom)

    # Evaluate model with noise
    results = evaluateModel(model=model, loader=noise_loader, device=device)

    # Remove noise from dataset transforms
    noiseTransform.transforms.remove(xfrom)

    # Update noise score
    noise_score += results["total_correct"]

  table = table.assign(noise_score=noise_score)

  # Filter result for the 'weight' variable only
  table = pd.DataFrame({label: table.xs("weight")})

  table.drop(["input", "output"], inplace=True)
  table.dropna(inplace=True)
  return table



def plotDataframe(table, title, plotPath):
  """
  Plot Panda dataframe.

  :param table: Panda dataframe returned by :func:`analyzeWeightPruning`
  :type table: :class:`pandas.DataFrame`
  :param title: Plot title
  :type title: str
  :param plotPath: Plot full path
  :type plotPath: str

  """
  plt.figure()
  axes = table.T.plot(subplots=True, sharex=True, grid=True, legend=True,
                      title=title, figsize=(8, 11))

  # Use fixed scale for "accuracy"
  accuracy = next(ax for ax in axes if ax.lines[0].get_label() == 'accuracy')
  accuracy.set_ylim(0.0, 1.0)

  plt.savefig(plotPath)
  plt.close()



def run(pool, expName, name, args):
  """
  Runs :func:`analyzeWeightPruning` in parallel and save the results

  :param pool: multiprocessing pool
  :param expName: Experiment name
  :param name: File/Plot name (i.e. 'weight_prunning')
  :param args: Argument list to be passed to :func:`analyzeWeightPruning`
  :return: panda dataframe with all the results

  """
  tables = pool.map(analyzeWeightPruning, args)
  merged = pd.concat(tables, axis=1).sort_index(axis=1)
  filename = "{}_{}".format(name, expName)
  plotDataframe(merged, filename, "{}.pdf".format(filename))
  print()
  print(filename)
  print(tabulate(merged, headers='keys', tablefmt='fancy_grid',
                 numalign="right"))
  merged.to_csv("{}.csv".format(filename))
  return merged



def main():
  # Initialize experiment options and parameters
  suite = SparseSpeechExperiment()
  suite.parse_opt()
  suite.parse_cfg()
  experiments = suite.options.experiments or suite.cfgparser.sections()

  pool = multiprocessing.Pool()

  for expName in experiments:
    path = suite.get_exp(expName)[0]
    results = suite.get_exps(path=path)

    # Build argument list for multiprocessing pool
    args = []
    for exp in results:
      params = suite.get_params(exp)
      params["datadir"] = suite.cfgparser.defaults()["datadir"]
      for i, minWeight in enumerate(np.linspace(0.0, 0.1, 21)):
        args.append((exp, params, minWeight, -1, i))

    args = np.array(args)

    # Analyze weight pruning alone. No dutycycle pruning
    args[:, 3] = -1  # set minDutycycle to -1 for all experiments
    run(pool, expName, "Weight Pruning", args)

    # Analyze dutycycle pruning units with dutycycle below 5% from target density
    args[:, 3] = 0.05  # set minDutycycle to 5% for all experiments
    run(pool, expName, "Dutycycle Pruning (5%)", args)

    # Analyze dutycycle pruning units with dutycycle below 10% from target density
    args[:, 3] = 0.10  # set minDutycycle to 10% for all experiments
    run(pool, expName, "Dutycycle Pruning (10%)", args)



if __name__ == '__main__':
  main()
