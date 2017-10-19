# Numenta Platform for Intelligent Computing (NuPIC)
# Copyright (C) 2016, Numenta, Inc.  Unless you have an agreement
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

"""
Use this script to generate the figures and results presented in (Cui, Ahmad &
Hawkins, 2016). For more information please refer to the original paper.
"""

import argparse
import matplotlib

matplotlib.use("Agg")

from argparse import RawDescriptionHelpFormatter
import re

RESULT_DIR_NAME = "results"
PLOTS_DIR_NAME = "plots"



def generateFigure4(cpuCount):
  """
  Prediction accuracy of HTM (red), LSTM (yellow, green, purple), ELM (blue),
  and TDNN (cyan) on an artificial data set. The data set contains four sixth
  order sequences and four seventh order sequences. Prediction accuracy is
  calculated as a moving average over the last 100 sequences. The sequences
  are changed after 10,000 elements have been seen (black dashed line). HTM
  sees each element once and learns continuously. ELM is trained continuously
  using a time lag of 10 steps. TDNN is retrained every 1000 elements (orange
  vertical lines) on the last 1000 elements (cyan). LSTM is either retrained
  every 1000 elements on the last 1000 elements (yellow) or 9000 elements
  (green), or continuously adapted using truncated BPTT (purple).
  """



def generateFigure5(cpuCount):
  """
  Final prediction accuracy as a function of the number of samples required to
  achieve final accuracy before (left) and after (right) modification of the
  sequences. Error bars represent standard deviations.
  """



def generateFigure6(cpuCount):
  """
  Performance on high-order sequence prediction tasks that require two (left)
  or four (right) simultaneous predictions. Shaded regions represent standard
  deviations (calculated with different sets of sequences). The data set
  contains four sets of sixth order sequences and four sets of seventh-order
  sequences.
  """



def generateFigure7A(cpuCount):
  """
  Prediction accuracy over learning with sequences of different orders
  """



def generateFigure7B(cpuCount):
  """
  Number of sequences required to achieve perfect prediction as a function
  of sequence order. The sequence data set contains four high-order sequences
  with the structure shown in Figure 3A.
  """



def generateFigure8A(cpuCount):
  """
  Prediction accuracy over learning with the presence of temporal noise for
  LSTM (gray) and HTM (black).
  """



def generateFigure8B(cpuCount):
  """
  HTM and LSTM are trained with clean sequences. Temporal noise was added
  after 12,000 elements.  The sequence data set is same as in Figure 4.
  """



def generateFigure9(cpuCount):
  """
  Robustness of the network to damage. The prediction accuracy after cell
  death is shown as a function of the fraction of cells that were removed
  from the network
  """



def generateFigure10(cpuCount):
  """
  Prediction of the New York City taxi passenger data. (A) Example
  portion of taxi passenger data (aggregated at 30 min intervals). The data
  have rich temporal patterns at both daily and weekly timescales. (B, C)
  Prediction error of different sequence prediction algorithms using two
  metrics: mean absolute percentage error (B), and negative log likelihood (C).
  """



def generateFigure11(cpuCount):
  """
  Prediction accuracy of LSTM and HTM after the introduction of
  new patterns. (A). The mean absolute percent error of HTM sequence memory
  (red) and LSTM networks (green, blue) after artificial manipulation of the
  data (black dashed line). The LSTM networks are retrained every week at the
  yellow vertical lines (B, C). Prediction error after the manipulation. HTM
  sequence memory has better accuracy on both the MAPE and the negative
  log-likelihood metrics.
"""



def _naturalSortKey(key):
  """
  Sort key using natural order.
  For example ["1","2","3","100"] instead of ["1", "100", "2", "3"]
  """
  return [int(s) if s.isdigit() else s for s in re.split("(\d+)", key)]



if __name__ == "__main__":

  # Map paper figures to experiment
  generateFigureFunc = {
    "4": generateFigure4,
    "5": generateFigure5,
    "6": generateFigure6,
    "7A": generateFigure7A,
    "7B": generateFigure7B,
    "8A": generateFigure8A,
    "8B": generateFigure8B,
    "9": generateFigure9,
    "10": generateFigure10,

  }
  figures = generateFigureFunc.keys()
  figures.sort(key=_naturalSortKey)

  parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=RawDescriptionHelpFormatter,
    epilog="-----------------------------------------------------------------------------\n"
           "Yuwei Cui, Subutai Ahmad and Jeff Hawkins (2016)\n"
           "Continuous Online Sequence Learning with an Unsupervised Neural Network Model,\n"
           "Published in Neural Computation, November 2016, Vol 28. No.11. 2016/11/01.\n"
           "http://www.mitpressjournals.org/doi/abs/10.1162/NECO_a_00893\n"
           "-----------------------------------------------------------------------------\n")

  parser.add_argument(
    "figure",
    metavar="FIGURE",
    nargs='?',
    type=str,
    default=None,
    choices=figures,
    help=("Specify the figure name to generate. Possible values are: %s " % figures)
  )
  parser.add_argument(
    "-c", "--cpuCount",
    default=None,
    type=int,
    metavar="number",
    help="Limit number of cpu cores.  Defaults to all available cores"
  )
  parser.add_argument(
    "-l", "--list",
    action='store_true',
    help='List all figures'
  )
  opts = parser.parse_args()

  if opts.list:
    for fig in figures:
      print fig, generateFigureFunc[fig].__doc__
  elif opts.figure is not None:
    generateFigureFunc[opts.figure](
      cpuCount=opts.cpuCount)
  else:
    parser.print_help()
