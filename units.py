"""
Units module
============

This module defines a simple class hierarchy for units that could be
used in an expanded version of the Battleships game.  Each unit
represents a piece on the battlefield with basic properties such as
name, hit points and attack range.  These classes are not integrated
into the current game logic but are provided as a starting point for
adding more complex behaviour (e.g. different attack patterns for
submarines vs tanks).
"""

from dataclasses import dataclass


@dataclass
class Unit:
    """Base class for all unit types."""
    name: str
    health: int
    attack_range: int

    def take_damage(self, damage: int) -> bool:
        """
        Reduce health by the given damage and return ``True`` if the unit is
        destroyed.

        Args:
            damage: How many hit points to subtract from the unit.

        Returns:
            A boolean indicating whether the unit's health has been reduced
            to zero or below.
        """
        self.health -= damage
        return self.health <= 0


@dataclass
class Ship(Unit):
    """A generic naval ship."""
    length: int = 1

    def __init__(
        self,
        name: str = "Ship",
        health: int = 1,
        attack_range: int = 1,
        length: int = 1,
    ) -> None:
        super().__init__(name, health, attack_range)
        self.length = length


@dataclass
class Submarine(Unit):
    """Represents a submarine with stealth capabilities."""
    submerged: bool = True

    def __init__(
        self,
        name: str = "Submarine",
        health: int = 1,
        attack_range: int = 1,
    ) -> None:
        super().__init__(name, health, attack_range)
        self.submerged = True


@dataclass
class Tank(Unit):
    """Represents a land tank unit."""
    armour: int = 2

    def __init__(
        self,
        name: str = "Tank",
        health: int = 3,
        attack_range: int = 1,
        armour: int = 2,
    ) -> None:
        super().__init__(name, health, attack_range)
        self.armour = armour


@dataclass
class Infantry(Unit):
    """Represents infantry troops."""
    def __init__(
        self,
        name: str = "Infantry",
        health: int = 1,
        attack_range: int = 1,
    ) -> None:
        super().__init__(name, health, attack_range)


@dataclass
class Artillery(Unit):
    """Represents an artillery unit with long range."""
    def __init__(
        self,
        name: str = "Artillery",
        health: int = 2,
        attack_range: int = 3,
    ) -> None:
        super().__init__(name, health, attack_range)
