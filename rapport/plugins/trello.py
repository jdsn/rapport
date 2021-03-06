# Copyright (c) 2013, Sascha Peilicke <saschpe@gmx.de>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program (see the file COPYING); if not, write to the
# Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA

"""
Trello plugin.
"""

import trolly.client
import trolly.member

import rapport.plugin
import rapport.util


# This is the public rapport Trello api key, which is used by default if you don't
# supply your own. In general you wouldn't need to either.
_RAPPORT_API_KEY="e8b72b9823082ad89dd7dfb40e8373bd"


class TrelloPlugin(rapport.plugin.Plugin):
    def __init__(self, api_key=_RAPPORT_API_KEY, user_auth_token=None, *args, **kwargs):
        super(TrelloPlugin, self).__init__(*args, **kwargs)

        #TODO: Ask the user for a token if he didn't provide one with trolly.authorise
        self._c = trolly.client.Client(api_key=_RAPPORT_API_KEY, user_auth_token=user_auth_token)

    def collect(self, timeframe):
        # Even though Trolly provides Board and Card classes, fetching
        # everything in one go should be faster. Also, we want to filter by
        # 'dateLastActivity', which would take too much round-trips with
        # Trolly's Card class.
        card_fields = "name,desc,closed,dateLastActivity,due"
        json = self._c.fetchJson("/members/{0}".format(self.login),
                                 query_params={"boards": "all",
                                               "cards": "all",
                                               "organizations": "all",
                                               "card_fields": card_fields})

        open_cards, closed_cards, due_cards = [], [], []
        for card in json["cards"]:
            last_activity = rapport.util.datetime_from_iso8601(card["dateLastActivity"])
            if timeframe.contains(last_activity):
                if card["closed"]:
                    closed_cards.append(card)
                else:
                    open_cards.append(card)
                if card["due"]:
                    due_cards.append(card)

        open_boards, closed_boards = [], []
        for board in json["boards"]:
            if board["closed"]:
                closed_boards.append(board)
            else:
                open_boards.append(board)

        return self._results({"boards": json["boards"],
                              "open_boards": open_boards,
                              "closed_boards": closed_boards,
                              "cards": json["cards"],
                              "open_cards": open_cards,
                              "closed_cards": closed_cards,
                              "due_cards": due_cards,
                              "organizations": json["organizations"]})


rapport.plugin.register("trello", TrelloPlugin)
