# ----------------------------------------------------------------------
# Numenta Platform for Intelligent Computing (NuPIC)
# Copyright (C) 2017, Numenta, Inc.  Unless you have an agreement
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
FROM python:2.7.14

# Add jessie-backports to source.list
RUN echo "deb http://ftp.debian.org/debian jessie-backports main" > /etc/apt/sources.list.d/jessie-backports.list

# Install R
RUN apt-get update && apt-get install -y \
    r-recommended=3.3.3-1~bpo8+1 r-base-core=3.3.3-1~bpo8+1 r-base=3.3.3-1~bpo8+1

# Install python dependencies
COPY requirements.txt /home/
RUN pip install -r /home/requirements.txt

# Install R dependencies
COPY install.r /home/
RUN R -f /home/install.r

# Copy context into container file system
COPY . /home/

ENV USER=root
WORKDIR /home/

