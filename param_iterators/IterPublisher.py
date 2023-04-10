# MIT License
 
# Copyright (c) 2023 Advanced Micro Devices, Inc.
 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from logger import logger
from param_iterators.IterSubscriber import IterSubscriber


class IterPublisher:
    """Publisher that calls update on Subscribers

    Implement this class to make an Iterator able to notify another iterator(subscriber) when it needs to update
    """

    def __init__(self, subscribers=[]):
        logger.debug("Initialized {} with subscribers: {}".format(self, subscribers))
        self.subscribers = subscribers

    def addSubscriber(self, subscriber):
        if not isinstance(subscriber, IterSubscriber):
            raise RuntimeError(
                "Attempted to add subscriber "
                + "'{}' that doesn't ".format(subscriber.__class__)
                + "inherit IterSubscriber"
            )
        self.subscribers.append(subscriber)

    def removeSubscriber(self, subscriber):
        self.subscribers.remove(subscriber)

    def notify(self):
        """Notifies all subscribers to incrment.

        Returns if any subscribers were notified
        """
        if len(self.subscribers) == 0:
            return False
        for sub in self.subscribers:
            sub.update()

        return True
