import unittest
from simulator.game import Game
from simulator.player import Player
from runtime.parser import LogParser
from simulator.enums import Zone

class TestLogParser(unittest.TestCase):
    def test_parse_coin_to_hand(self):
        # 1. Setup Empty Game (Listen Mode)
        game = Game()
        p1 = Player("Player 1", game)
        p2 = Player("Player 2", game)
        game.players = [p1, p2]
        
        # Ensure players are reset/empty
        for p in game.players:
            p.hand = []
            p.board = []
            
        parser = LogParser(game)
        
        # 2. Simulate Log Line: Creating/Drawing the Coin
        # Real log sample: 
        # D 02:22:20.123456 GameState.DebugPrintPower() - TAG_CHANGE Entity=[id=60 cardId=GAME_005 name=Coin] tag=ZONE value=HAND
        log_line = "D 00:00:00.000000 GameState.DebugPrintPower() - TAG_CHANGE Entity=[id=60 cardId=GAME_005 name=Coin] tag=ZONE value=HAND"
        
        parser.parse_line(log_line)
        
        # 3. Assertions
        # Player 0 (default controller in current simple parser info) should have the coin
        p1_check = game.players[0]
        
        self.assertEqual(len(p1_check.hand), 1, "Player should have 1 card in hand")
        coin = p1_check.hand[0]
        
        self.assertEqual(coin.card_id, "GAME_005")
        self.assertEqual(coin.entity_id, 60)
        self.assertEqual(coin.zone, Zone.HAND)
        
    def test_parse_play_minion(self):
        # 1. Setup
        game = Game()
        p1 = Player("Player 1", game)
        p2 = Player("Player 2", game)
        game.players = [p1, p2]
        
        parser = LogParser(game)
        p1 = game.players[0]
        
        # 2. Put card in hand first
        log_draw = "D 00:00:00.000000 GameState.DebugPrintPower() - TAG_CHANGE Entity=[id=20 cardId=CS2_120 name=RiverCrocolisk] tag=ZONE value=HAND"
        parser.parse_line(log_draw)
        
        self.assertEqual(len(p1.hand), 1)
        self.assertEqual(len(p1.board), 0)
        
        # 3. Play it (Hand -> Play)
        log_play = "D 00:00:00.000000 GameState.DebugPrintPower() - TAG_CHANGE Entity=[id=20 cardId=CS2_120 name=RiverCrocolisk] tag=ZONE value=PLAY"
        parser.parse_line(log_play)
        
        self.assertEqual(len(p1.hand), 0, "Hand should be empty")
        self.assertEqual(len(p1.board), 1, "Board should have 1 minion")
        self.assertEqual(p1.board[0].zone, Zone.PLAY)

if __name__ == "__main__":
    unittest.main()
