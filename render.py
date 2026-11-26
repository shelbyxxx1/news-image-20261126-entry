from __future__ import annotations

import argparse
import hashlib
import math
from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
SIZE = 1024
SCALE = 3
PAPER = "#f6f1e5"
INK = "#191919"
RED = "#7f1d1d"
GREEN = "#14532d"
SEA = "#5b7186"
MUTED = "#666052"
RULE = "#b7ad9a"
NAVY = "#132535"
CREAM = "#e7dac0"


@dataclass(frozen=True)
class Story:
    number: int
    region: str
    field: str
    headline: str
    deck: str = ""
    kicker: str = ""


STORIES = (
    Story(1, "MIDDLE EAST", "War & security", "Missiles over Riyadh",
          "Yemen's Houthis claim strikes on the Ras Tanura refinery and Riyadh's financial district; the Saudi-led coalition says it destroyed two ballistic missiles over the capital, a day after attacks on the Jeddah and Jazan ports. Turkiye condemns the attack."),
    Story(2, "AMERICAS", "Markets & business", "US proposes tariffs on 14 partners",
          "China hit hardest at nearly 45% in a new Section 301 round; the EU, Japan and India also named.", "MARKETS"),
    Story(3, "AFRICA", "Disaster", "Cairo tanker fire kills at least 31",
          "A fuel tanker overturns and bursts into flames on the ring road; about 21 hurt.", "DISASTER"),
    Story(4, "AMERICAS", "Culture", "Macy's parade postponed — a first",
          "The 100th Thanksgiving parade moves to Saturday 28 Nov as a nor'easter bears down on New York.", "CULTURE"),
    Story(5, "EUROPE", "War & security", "Ukraine hits five jets at Russian airbase",
          "Three MiG-31s and two Su-34s damaged at Savasleyka; Kyiv hit by ballistic missiles.", "WAR"),
    Story(6, "MIDDLE EAST", "War & security", "US tells citizens to leave Iran",
          "War fears grow as Tehran says Israel is trying to drag America into a new war.", "WAR"),
    Story(7, "ASIA", "Tech & AI", "First Pakistani in space reaches Tiangong",
          "Muhammad Zeeshan Ali boards China's space station aboard Shenzhou-24.", "TECH"),
    Story(8, "EUROPE", "Politics", "Nearly 2,000 migrants reach Canary Islands",
          "El Hierro records a record single-day arrival of almost 2,000 people.", "WORLD"),
    Story(9, "AMERICAS", "Markets & business", "AI sell-off drags Nasdaq near bear market",
          "Nvidia falls 3.9% as selling in AI-linked shares continues.", "MARKETS"),
    Story(10, "MIDDLE EAST", "War & security", "Israeli strikes in Gaza kill a Hamas security chief."),
    Story(11, "EUROPE", "Politics", "EU leaders clash in Brussels over a €45bn Ukraine loan and the next budget."),
    Story(12, "ASIA", "Politics", "Kim Jong Un urges a wider spread of tactical nuclear weapons; North Korea expels the Swiss envoy."),
    Story(13, "ASIA", "Disaster", "Rescuers race to find 13 miners trapped in a flooded illegal gold mine in Bogor, Indonesia."),
    Story(14, "AMERICAS", "Justice", "Puerto Rico's Supreme Court cancels the Luma Energy power contract, 5–4."),
    Story(15, "MIDDLE EAST", "War & security", "ISIL suicide attack kills two security personnel in Hasakah, Syria."),
    Story(16, "EUROPE", "Politics", "Spain heads to a snap vote on Sunday as Sanchez faces a conservative challenge."),
    Story(17, "AFRICA", "Politics", "Zambia bans a protest against a push to remove term limits."),
    Story(18, "EUROPE", "Markets & business", "London Underground faces severe disruption from a tube strike on Thursday and Friday."),
    Story(19, "MIDDLE EAST", "War & security", "A tanker catches fire after hitting a mine in the Strait of Hormuz."),
    Story(20, "AMERICAS", "Justice", "A US court finds Chinese tech giant Huawei guilty of theft."),
    Story(21, "WORLD", "Politics", "Australia enacts sweeping online safety laws with heavy fines for tech giants."),
    Story(22, "EUROPE", "Politics", "Poland urges NATO to shoot down Russian missiles over Ukraine; AWACS deployment approved."),
    Story(23, "EUROPE", "Politics", "Russia adopts its largest military budget since Soviet times."),
    Story(24, "CULTURE", "Culture", "Duran Duran guitarist Andy Taylor dies aged 65."),
    Story(25, "ASIA", "Disaster", "A Hong Kong renovation ends in a blaze that kills 168 people."),
    Story(26, "AMERICAS", "War & security", "The US Army calls its controlled blast of explosives in Iowa a 'huge success'."),
    Story(27, "WORLD", "Tech & AI", "The FCC clears SpaceX to build orbital data centres with up to a million satellites."),
    Story(28, "MIDDLE EAST", "Justice", "Judges suggest dropping a Netanyahu bribery charge in Case 4000."),
    Story(29, "EUROPE", "Politics", "A new UK-EU treaty carries a 10-year termination clause, the BBC understands."),
    Story(30, "AFRICA", "Politics", "DR Congo demands answers over a Ugandan general's threats."),
    Story(31, "EUROPE", "Justice", "BBC finds a German boat dealer suspected of supplying Channel smuggling gangs."),
    Story(32, "MIDDLE EAST", "Justice", "Desperate appeals from women on death row in Iran after the protests."),
    Story(33, "ASIA", "Politics", "Bangladesh's Hasina vows to come back despite a death sentence."),
    Story(34, "EUROPE", "War & security", "Two Libyan soldiers die of wounds from the Benghazi port drone attack."),
    Story(35, "MIDDLE EAST", "Politics", "An Etihad flight to Tel Aviv turns back to Abu Dhabi amid the Saudi-Houthi crisis."),
    Story(36, "MIDDLE EAST", "Justice", "Iraq sentences eight French citizens to life for ISIS affiliation."),
    Story(37, "AMERICAS", "Politics", "The US risks a third government shutdown over funding for the Iran war."),
    Story(38, "AFRICA", "Politics", "Libya publishes its sea-boundary agreement with Turkiye."),
    Story(39, "EUROPE", "War & security", "Russia attacks Kryvyi Rih with drones and hits a mall."),
    Story(40, "MIDDLE EAST", "Politics", "Fresh Israeli gates could cut off 70,000 Palestinians in the West Bank, a mayor warns."),
    Story(41, "AFRICA", "War & security", "African insurgents take the war to the skies with commercial drones."),
    Story(42, "SPORT", "Sport", "Champions League: Liverpool beat Club Brugge 3–0; Lille beat Bayern Munich 2–1."),
    Story(43, "CULTURE", "Culture", "Jennifer Barreto wins Miss Universe 2026."),
)

REGIONS = ("MIDDLE EAST", "EUROPE", "AMERICAS", "ASIA", "AFRICA", "WORLD", "SPORT", "CULTURE")
FIELDS = ("War & security", "Politics", "Justice", "Markets & business", "Tech & AI", "Disaster", "Sport", "Culture")

DATE_CHECK = (
    "DATE CHECK — Left out on purpose because they broke before today: the Russian corvette Merkury sinking off Benghazi (22–23 Nov); "
    "Jensen Huang reinstated as Nvidia CEO (23 Nov); the COP31 talks collapsing (22–23 Nov); the Trump–Xi–Putin summit in Shenzhen ending (21 Nov); "
    "CrowdStrike buying Zscaler for $44bn (23 Nov); the Women's World Cup 2031/2035 hosts named (24 Nov)."
)

FOOTER = (
    "Drawn entirely by program · Set in Noto Serif Display & Noto Sans Condensed · Every story happened or was first reported Thursday 26 November 2026. "
    "Sources: Reuters, BBC, CNN, AP, Al Jazeera, OneTurn, DailySummaryOf. Original drawings."
)

FONT_FILES = {
    "masthead": ("noto/NotoSerifDisplay-Black.ttf", "dejavu/DejaVuSerif-Bold.ttf"),
    "headline": ("noto/NotoSerifDisplay-Bold.ttf", "dejavu/DejaVuSerif-Bold.ttf"),
    "compact": ("noto/NotoSerifDisplay-CondensedBold.ttf", "dejavu/DejaVuSerifCondensed-Bold.ttf"),
    "body": ("noto/NotoSans-Condensed.ttf", "dejavu/DejaVuSansCondensed.ttf"),
    "narrow": ("noto/NotoSans-ExtraCondensed.ttf", "dejavu/DejaVuSansCondensed.ttf"),
    "bold": ("noto/NotoSans-CondensedBold.ttf", "dejavu/DejaVuSansCondensed-Bold.ttf"),
}


@lru_cache(maxsize=None)
def font(kind: str, size: float) -> ImageFont.FreeTypeFont:
    for relative in FONT_FILES[kind]:
        path = Path("/usr/share/fonts/truetype") / relative
        if path.is_file():
            return ImageFont.truetype(str(path), round(size * SCALE), layout_engine=ImageFont.Layout.BASIC)
    raise FileNotFoundError(f"No Noto or DejaVu font for {kind}")


def width(text: str, kind: str, size: float) -> float:
    return font(kind, size).getlength(text) / SCALE


def wrap(text: str, available: float, kind: str, size: float) -> list[str]:
    lines = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}" if current else word
        if width(candidate, kind, size) > available and current:
            lines.append(current)
            current = word
        else:
            current = candidate
        if width(current, kind, size) > available:
            raise ValueError(f"Word too wide: {word!r}")
    if current:
        lines.append(current)
    return lines


class Page:
    def __init__(self) -> None:
        self.image = Image.new("RGB", (SIZE * SCALE, SIZE * SCALE), PAPER)
        self.draw = ImageDraw.Draw(self.image)
        self.text_boxes = []
        self.minimum_size = 100.0

    def rect(self, box, fill, outline=None, stroke=1):
        self.draw.rectangle(tuple(round(value * SCALE) for value in box), fill=fill, outline=outline, width=max(1, round(stroke * SCALE)))

    def ellipse(self, box, fill, outline=None, stroke=1):
        self.draw.ellipse(tuple(round(value * SCALE) for value in box), fill=fill, outline=outline, width=max(1, round(stroke * SCALE)))

    def polygon(self, points, fill):
        self.draw.polygon([(round(left * SCALE), round(top * SCALE)) for left, top in points], fill=fill)

    def line(self, points, fill=RULE, stroke=0.6):
        self.draw.line([(round(left * SCALE), round(top * SCALE)) for left, top in points], fill=fill, width=max(1, round(stroke * SCALE)), joint="curve")

    def text(self, left, top, text, kind="body", size=11, fill=INK, align="left", check=True):
        face = font(kind, size)
        box = face.getbbox(text)
        text_width = face.getlength(text) / SCALE
        if align == "center":
            left -= text_width / 2
        elif align == "right":
            left -= text_width
        origin = (round(left * SCALE) - box[0], round(top * SCALE) - box[1])
        self.draw.text(origin, text, font=face, fill=fill)
        bounds = (left, top, left + (box[2] - box[0]) / SCALE, top + (box[3] - box[1]) / SCALE)
        if check:
            assert bounds[0] >= 20 and bounds[1] >= 20 and bounds[2] <= 1004 and bounds[3] <= 1004, (text, bounds)
            self.text_boxes.append((bounds, text))
        self.minimum_size = min(self.minimum_size, size)
        return bounds[3]

    def paragraph(self, left, top, text, available, kind="body", size=11, leading=12, fill=INK, max_lines=None):
        lines = wrap(text, available, kind, size)
        if max_lines is not None:
            assert len(lines) <= max_lines, (text, len(lines), max_lines)
        for index, line in enumerate(lines):
            self.text(left, top + index * leading, line, kind, size, fill)
        return top + len(lines) * leading

    def star(self, left, top, radius, fill):
        points = []
        for index in range(16):
            angle = math.pi * index / 8
            distance = radius if index % 2 == 0 else radius * 0.26
            points.append((left + math.cos(angle) * distance, top + math.sin(angle) * distance))
        self.polygon(points, fill)


def bezier(start, control, finish, steps=64):
    points = []
    for index in range(steps + 1):
        fraction = index / steps
        points.append(((1 - fraction) ** 2 * start[0] + 2 * (1 - fraction) * fraction * control[0] + fraction ** 2 * finish[0],
                       (1 - fraction) ** 2 * start[1] + 2 * (1 - fraction) * fraction * control[1] + fraction ** 2 * finish[1]))
    return points


def draw_riyadh(page: Page, left, top, available, height):
    page.rect((left, top, left + available, top + height), NAVY)
    page.rect((left, top + height * 0.53, left + available, top + height), "#203743")
    for index in range(26):
        star_x = left + 8 + ((index * 71) % int(available - 16))
        star_y = top + 4 + ((index * 17) % max(5, int(height * 0.5)))
        page.ellipse((star_x, star_y, star_x + 0.65, star_y + 0.65), "#91a2ab")
    floor = top + height
    for index in range(31):
        building_x = left + index * available / 31
        building_width = available / 31 - 2
        building_height = 9 + ((index * 13 + 5) % 21)
        page.rect((building_x, floor - building_height, building_x + building_width, floor), "#101d26")
        for window in range(2):
            page.rect((building_x + 3, floor - building_height + 4 + window * 6, building_x + 4, floor - building_height + 5 + window * 6), "#c8aa70")
    tower_x = left + available * 0.49
    tower_top = top + height * 0.19
    page.polygon([(tower_x - 10, floor), (tower_x - 8, tower_top + 5), (tower_x - 5, tower_top),
                  (tower_x + 6, tower_top), (tower_x + 9, tower_top + 5), (tower_x + 11, floor)], "#637d87")
    page.polygon([(tower_x - 5, tower_top + 3), (tower_x + 6, tower_top + 3),
                  (tower_x + 4, tower_top + 13), (tower_x + 1, tower_top + 15),
                  (tower_x - 3, tower_top + 12)], NAVY)
    page.line([(tower_x - 8, floor - 2), (tower_x - 6, tower_top + 17)], "#c0cbd0", 0.65)
    for index, fraction in enumerate((0.27, 0.76)):
        burst = (left + available * fraction, top + height * (0.25 + 0.13 * index))
        start = (left + available * (0.12 + 0.8 * index), floor - 4)
        page.line(bezier(start, (left + available * (0.12 + 0.75 * index), top + 9), burst), "#718b96", 3)
        page.line(bezier(start, (left + available * (0.12 + 0.75 * index), top + 9), burst), "#f5dfac", 1)
        approach = (left + available * (0.43 + index * 0.2), top + 4)
        page.line([approach, burst], "#c8d1cb", 0.7)
        page.star(*burst, 8, "#cf8849")
        page.star(*burst, 5, "#fff0bc")
    page.rect((left + 6, floor - 17, left + 100, floor - 3), NAVY)
    page.text(left + 10, floor - 15, "RIYADH · NIGHT SKY", "bold", 11, CREAM)


def draw_stamp(page, left, top, available, height):
    page.rect((left, top, left + available, top + height), "#d8dfd9")
    for index, color in enumerate((SEA, "#b5a680", GREEN, "#9d6453")):
        container_x = left + 8 + index * 43
        level = 5 if index % 2 else 10
        page.rect((container_x, top + level, container_x + 41, top + height - 3), color)
        for rib in range(1, 8):
            page.line([(container_x + rib * 5, top + level + 1), (container_x + rib * 5, top + height - 4)], CREAM, 0.3)
    page.rect((left + available - 76, top + 3, left + available - 7, top + height - 3), PAPER, RED, 1.5)
    page.text(left + available - 41.5, top + 5, "TARIFFS", "bold", 13, RED, "center")


def draw_fire(page, left, top, available, height):
    page.rect((left, top, left + available, top + height), "#dfc9a9")
    page.rect((left, top + height - 8, left + available, top + height), "#6f6c60")
    page.line([(left + 5, top + height - 4), (left + available - 5, top + height - 4)], CREAM, 0.6)
    truck_x = left + 42
    page.rect((truck_x, top + 10, truck_x + 97, top + height - 6), "#424c4a")
    page.ellipse((truck_x + 6, top + 7, truck_x + 78, top + height - 8), "#9faeaa")
    page.rect((truck_x + 82, top + 8, truck_x + 106, top + height - 6), GREEN)
    page.rect((truck_x + 87, top + 10, truck_x + 102, top + 15), "#d4e0dc")
    for offset in (17, 65, 92):
        page.ellipse((truck_x + offset - 3, top + height - 9, truck_x + offset + 3, top + height - 3), INK)
    for index in range(6):
        flame_x = left + 142 + index * 9
        page.polygon([(flame_x - 7, top + height - 8), (flame_x - 6, top + 9), (flame_x - 1, top + 13),
                      (flame_x + 3, top + 2 + index % 3 * 2), (flame_x + 8, top + height - 8)], "#b4572b")
        page.polygon([(flame_x - 3, top + height - 8), (flame_x + 2, top + 12), (flame_x + 5, top + height - 8)], "#edbf64")


def draw_parade(page, left, top, available, height):
    page.rect((left, top, left + available, top + height), "#c7d3d7")
    for index in range(12):
        building_x = left + index * 20
        page.rect((building_x, top + 9 + index % 3 * 3, building_x + 16, top + height), "#889a9d")
    for index in range(19):
        rain_x = left + 5 + index * 12
        page.line([(rain_x, top + 1), (rain_x - 3, top + 8)], "#f0eee2", 0.6)
    balloon_x = left + available * 0.48
    page.ellipse((balloon_x - 26, top + 2, balloon_x + 22, top + height - 5), "#a55643")
    page.ellipse((balloon_x - 30, top + 3, balloon_x - 15, top + 15), "#a55643")
    page.ellipse((balloon_x + 10, top + 3, balloon_x + 26, top + 15), "#a55643")
    page.ellipse((balloon_x - 10, top + 10, balloon_x - 8, top + 12), INK)
    page.ellipse((balloon_x + 5, top + 10, balloon_x + 7, top + 12), INK)
    for offset in (-14, 11):
        page.line([(balloon_x + offset, top + height - 6), (balloon_x + offset - 5, top + height)], PAPER, 0.6)


def plane(page, center_x, center_y, factor, color):
    points = [(0, -8), (2, -2), (10, 3), (10, 5), (2, 3), (2, 7), (5, 9),
              (-5, 9), (-2, 7), (-2, 3), (-10, 5), (-10, 3), (-2, -2)]
    page.polygon([(center_x + horizontal * factor, center_y + vertical * factor) for horizontal, vertical in points], color)


def draw_jets(page, left, top, available, height):
    page.rect((left, top, left + available, top + height), "#293846")
    page.polygon([(left, top + height), (left + 32, top + 8), (left + available - 32, top + 8), (left + available, top + height)], "#5d686c")
    for index in range(5):
        plane(page, left + 28 + index * (available - 56) / 4, top + height / 2 - 1, 0.85, "#c5c8bd")
    page.line([(left + 8, top + height - 2), (left + available - 8, top + height - 2)], "#d0bd90", 0.6)


def draw_embassy(page, left, top, available, height):
    page.rect((left, top, left + available, top + height), "#c9d5cd")
    page.rect((left + 22, top + 5, left + 143, top + height), "#bac0aa")
    page.polygon([(left + 15, top + 9), (left + 82, top + 1), (left + 150, top + 9)], GREEN)
    for index in range(10):
        gate_x = left + 48 + index * 7
        page.line([(gate_x, top + 10), (gate_x, top + height)], GREEN, 1)
    page.line([(left + 44, top + 11), (left + 115, top + 11)], GREEN, 1.5)
    for offset in (31, 127):
        page.rect((left + offset, top + 11, left + offset + 8, top + height), GREEN)
    plane(page, left + available - 37, top + 9, 0.83, NAVY)
    page.line([(left + 150, top + 23), (left + available - 41, top + 13)], PAPER, 1.1)


def draw_space(page, left, top, available, height):
    page.rect((left, top, left + available, top + height), NAVY)
    page.ellipse((left - 14, top + 14, left + available + 20, top + height + 70), SEA)
    page.ellipse((left - 8, top + 18, left + available + 12, top + height + 70), "#8da9ac")
    station_x = left + available / 2
    for direction in (-1, 1):
        panel_x = station_x + direction * 24
        page.rect((panel_x - 24, top + 4, panel_x + 24, top + 15), "#c4ac68")
        for offset in (-16, -8, 0, 8, 16):
            page.line([(panel_x + offset, top + 4), (panel_x + offset, top + 15)], NAVY, 0.5)
        page.line([(panel_x - 24, top + 9), (panel_x + 24, top + 9)], NAVY, 0.5)
    page.rect((station_x - 13, top + 8, station_x + 13, top + 13), PAPER)
    page.rect((station_x - 4, top + 2, station_x + 4, top + 20), PAPER)
    page.ellipse((station_x - 3, top + 5, station_x + 3, top + 10), "#be7357")


def draw_boats(page, left, top, available, height):
    page.rect((left, top, left + available, top + height), "#cedbd6")
    page.rect((left, top + 10, left + available, top + height), SEA)
    page.polygon([(left + available - 91, top + height), (left + available - 56, top + 10),
                  (left + available - 41, top + 3), (left + available - 5, top + 10), (left + available, top + height)], GREEN)
    page.polygon([(left + available - 91, top + height), (left + available - 58, top + 19),
                  (left + available - 37, top + 17), (left + available - 20, top + height)], "#c8b68d")
    for index in range(3):
        boat_x = left + 19 + index * 35
        boat_y = top + 15 + index % 2 * 4
        page.polygon([(boat_x, boat_y), (boat_x + 25, boat_y), (boat_x + 20, boat_y + 5), (boat_x + 5, boat_y + 5)], "#eee4ca")
        for passenger in range(4):
            page.ellipse((boat_x + 5 + passenger * 4, boat_y - 3, boat_x + 7 + passenger * 4, boat_y - 1), NAVY)


def draw_chart(page, left, top, available, height):
    page.rect((left, top, left + available, top + height), "#dddccd")
    for index in range(16):
        tower_x = left + index * 15
        tower_height = 4 + index * 7 % 14
        page.rect((tower_x, top + height - tower_height, tower_x + 11, top + height), "#a1aaa4")
    points = [(left + available * fraction, top + height * level) for fraction, level in
              ((0.04, 0.16), (0.18, 0.32), (0.28, 0.23), (0.4, 0.52), (0.51, 0.38), (0.64, 0.66), (0.76, 0.53), (0.94, 0.86))]
    page.line(points, RED, 2.6)
    end_x, end_y = points[-1]
    page.polygon([(end_x - 9, end_y - 2), (end_x + 1, end_y + 2), (end_x - 1, end_y - 8)], RED)


ILLUSTRATIONS = (draw_stamp, draw_fire, draw_parade, draw_jets, draw_embassy, draw_space, draw_boats, draw_chart)

HEADLINE_LINES = (
    ("US proposes tariffs", "on 14 partners"),
    ("Cairo tanker fire", "kills at least 31"),
    ("Macy's parade", "postponed — a first"),
    ("Ukraine hits five jets", "at Russian airbase"),
    ("US tells citizens", "to leave Iran"),
    ("First Pakistani in space", "reaches Tiangong"),
    ("Nearly 2,000 migrants", "reach Canary Islands"),
    ("AI sell-off drags Nasdaq", "near bear market"),
)


def draw_strip(page, illustration, left, top, available, height):
    layer = Page()
    illustration(layer, left, top, available, height)
    crop_box = tuple(round(value * SCALE) for value in (left, top, left + available, top + height))
    page.image.paste(layer.image.crop(crop_box), crop_box[:2])


def draw_count_bar(page, top, names, counts, uppercase=False):
    labels = [f"{name} {counts[name]}" for name in names]
    if uppercase:
        labels = [label.upper() for label in labels]
    total_width = sum(width(label, "bold", 11) for label in labels)
    gap = (976 - total_width) / (len(labels) - 1)
    assert gap >= 10, (labels, gap)
    cursor = 24
    for index, label in enumerate(labels):
        page.text(cursor, top, label, "bold", 11, GREEN if uppercase else MUTED)
        cursor += width(label, "bold", 11)
        if index < len(labels) - 1:
            page.ellipse((cursor + gap / 2 - 1, top + 4, cursor + gap / 2 + 1, top + 6), RULE)
            cursor += gap


def draw_header(page):
    page.text(24, 21, "LATE EDITION · ALL THE NEWS OF ONE DAY ON ONE PAGE", "bold", 11)
    page.text(1000, 21, "No. 2026-330", "body", 11, INK, "right")
    page.line([(24, 36), (1000, 36)], INK, 0.8)
    page.text(512, 41, "THE WORLD IN ONE DAY", "masthead", 74, INK, "center")
    page.rect((24, 103, 1000, 126), RED)
    page.text(512, 108, "THURSDAY, 26 NOVEMBER 2026 — 43 STORIES · 8 REGIONS · ONE PAGE", "bold", 14, PAPER, "center")
    regions = Counter(story.region for story in STORIES)
    fields = Counter(story.field for story in STORIES)
    assert sum(regions.values()) == sum(fields.values()) == 43
    draw_count_bar(page, 131, REGIONS, regions, True)
    draw_count_bar(page, 145, FIELDS, fields)
    page.line([(24, 160), (1000, 160)], INK, 1.4)


def draw_lead(page):
    page.text(24, 167, "MIDDLE EAST · WAR & SECURITY — THE LEAD", "bold", 11, RED)
    page.text(24, 182, STORIES[0].headline, "headline", 55)
    deck_end = page.paragraph(24, 243, STORIES[0].deck, 976, size=13, leading=14, max_lines=2)
    assert deck_end <= 271
    draw_riyadh(page, 24, 278, 465, 53)
    bullet_texts = (
        "A blast was heard in Sanaa after air strikes near the airport.",
        "An Etihad flight to Tel Aviv turned back to Abu Dhabi amid the crisis.",
    )
    cursor = 278
    for text in bullet_texts:
        page.rect((505, cursor + 4, 508, cursor + 7), RED)
        cursor = page.paragraph(517, cursor, text, 483, "body", 12, 14, max_lines=2) + 5
    page.paragraph(505, cursor + 1, "Houthi attacks on Saudi ports and the refinery mark a sharp escalation (story 19).", 495, "body", 11, 12, fill=MUTED, max_lines=2)
    page.line([(24, 338), (1000, 338)], INK, 1)


def draw_grid(page):
    gap = 16
    cell_width = (976 - 3 * gap) / 4
    row_height = 106
    for index, story in enumerate(STORIES[1:9]):
        column = index % 4
        row = index // 4
        left = 24 + column * (cell_width + gap)
        top = 342 + row * (row_height + 8)
        if column:
            page.line([(left - 8, top), (left - 8, top + row_height)], RULE, 0.5)
        draw_strip(page, ILLUSTRATIONS[index], left, top, cell_width, 22)
        page.text(left, top + 26, f"{story.number} · {story.region} · {story.kicker}", "bold", 11, RED)
        assert " ".join(HEADLINE_LINES[index]) == story.headline
        for line_index, line in enumerate(HEADLINE_LINES[index]):
            assert width(line, "compact", 18) <= cell_width
            page.text(left, top + 40 + line_index * 19, line, "compact", 18)
        deck_end = page.paragraph(left, top + 80, story.deck, cell_width, "body", 11, 12, max_lines=2)
        assert deck_end <= top + row_height + 1, (story.number, deck_end, top + row_height)
    page.line([(24, 568), (1000, 568)], INK, 1)


def draw_numbers(page):
    figures = (
        ("2", "ballistic missiles destroyed over Riyadh"),
        ("31", "killed in the Cairo tanker fire"),
        ("14", "trading partners face new US tariffs"),
        ("100th", "Macy's parade postponed, a first"),
        ("5", "military jets damaged at Savasleyka"),
        ("~2,000", "migrants reach the Canaries in a day"),
    )
    for index, (figure, label) in enumerate(figures):
        left = 24 + index * 976 / 6
        center = left + 976 / 12
        if index:
            page.line([(left, 575), (left, 628)], RULE, 0.5)
        page.text(center, 574, figure, "headline", 26, RED, "center")
        lines = wrap(label, 150, "body", 11)
        assert len(lines) <= 2
        for row, line in enumerate(lines):
            page.text(center, 605 + 12 * row, line, "body", 11, INK, "center")
    page.line([(24, 634), (1000, 634)], INK, 1)


CONTINENTS = (
    ((-168, 71), (-142, 71), (-132, 57), (-123, 50), (-126, 40), (-114, 29), (-99, 17), (-87, 20), (-81, 9), (-77, 9), (-83, 23), (-80, 33), (-67, 44), (-56, 52), (-62, 61), (-80, 66), (-95, 73), (-120, 73), (-152, 61)),
    ((-73, 59), (-52, 60), (-23, 76), (-39, 83), (-62, 81)),
    ((-80, 11), (-67, 9), (-51, 1), (-35, -6), (-39, -21), (-50, -30), (-60, -53), (-70, -54), (-75, -37), (-70, -18), (-81, -5)),
    ((-11, 36), (-9, 44), (3, 49), (7, 56), (23, 71), (34, 70), (29, 59), (42, 54), (51, 58), (62, 70), (110, 77), (142, 73), (180, 65), (167, 53), (146, 44), (142, 35), (126, 34), (121, 22), (110, 18), (106, 8), (100, 2), (92, 20), (80, 8), (72, 20), (62, 25), (53, 17), (42, 12), (35, 30), (25, 36), (12, 41), (1, 37)),
    ((-17, 34), (4, 37), (23, 32), (32, 31), (35, 18), (50, 11), (43, 0), (39, -15), (29, -34), (17, -35), (11, -19), (6, -3), (-9, 4), (-17, 17)),
    ((112, -12), (135, -11), (145, -17), (153, -27), (146, -39), (130, -33), (115, -35)),
    ((47, -13), (51, -17), (48, -27), (44, -25)),
    ((129, 31), (141, 45), (146, 43), (140, 34)),
    ((96, 5), (106, -5), (118, -8), (134, -6), (142, -9), (132, -2), (120, 2), (108, 6)),
    ((166, -34), (178, -37), (172, -46), (166, -46)),
    ((-10, 50), (-8, 59), (-2, 59), (1, 51)),
)


def inside(point, polygon):
    point_x, point_y = point
    result = False
    previous_x, previous_y = polygon[-1]
    for next_x, next_y in polygon:
        if (next_y > point_y) != (previous_y > point_y):
            crossing = (previous_x - next_x) * (point_y - next_y) / (previous_y - next_y) + next_x
            if point_x < crossing:
                result = not result
        previous_x, previous_y = next_x, next_y
    return result


def draw_map(page, left, top, available, height):
    page.text(left, top, "WHERE IT HAPPENED", "bold", 14, GREEN)
    map_top = top + 23
    map_height = 125
    def project(longitude, latitude):
        return left + (longitude + 180) / 360 * available, map_top + (85 - latitude) / 145 * map_height

    for latitude in range(-55, 81, 6):
        for longitude in range(-174, 180, 6):
            dot_x, dot_y = project(longitude, latitude)
            on_land = any(inside((longitude, latitude), polygon) for polygon in CONTINENTS)
            radius = 0.8 if on_land else 0.35
            color = SEA if on_land else "#d9d8cb"
            page.ellipse((dot_x - radius, dot_y - radius, dot_x + radius, dot_y + radius), color)
    pins = (
        (1, 46.7, 24.7, 0.63, 1.04),
        (2, -77.0, 38.9, 0.12, 0.52),
        (3, 31.2, 30.0, 0.40, 1.04),
        (4, -74.0, 40.7, 0.19, 0.08),
        (5, 42.3, 55.4, 0.56, 0.02),
        (6, 51.4, 35.7, 0.82, 0.77),
        (7, 116.4, 39.9, 0.92, 0.21),
        (8, -18.0, 27.7, 0.24, 0.96),
        (9, -74.0, 40.7, 0.37, 0.20),
    )
    for number, longitude, latitude, horizontal, vertical in pins:
        spot_x, spot_y = project(longitude, latitude)
        label_x = left + horizontal * available
        label_y = map_top + vertical * map_height
        page.line([(spot_x, spot_y), (label_x, label_y)], RED, 0.55)
        page.ellipse((spot_x - 1.3, spot_y - 1.3, spot_x + 1.3, spot_y + 1.3), RED)
        page.ellipse((label_x - 7, label_y - 7, label_x + 7, label_y + 7), RED)
        page.text(label_x, label_y - 4.5, str(number), "bold", 11, PAPER, "center")
    legend = (
        "1 Riyadh  ·  2 Washington",
        "3 Cairo  ·  4 New York",
        "5 Savasleyka  ·  6 Tehran",
        "7 Beijing/Tiangong",
        "8 Canary Islands  ·  9 Wall Street",
    )
    for index, line in enumerate(legend):
        page.text(left, map_top + map_height + 18 + index * 14, line, "body", 11)
    assert map_top + map_height + 18 + 5 * 14 <= top + height


def brief_columns(available, max_height):
    entries = []
    for story in STORIES[9:]:
        text = f"{story.number} {story.region} — {story.headline}"
        lines = wrap(text, available, "narrow", 11)
        entries.append((story, lines, len(lines) * 11.5 + 0.5))
    best = None
    for first in range(1, len(entries) - 1):
        for second in range(first + 1, len(entries)):
            columns = (entries[:first], entries[first:second], entries[second:])
            heights = [sum(entry[2] for entry in column) for column in columns]
            score = (max(heights), max(heights) - min(heights), first, second)
            if best is None or score < best[0]:
                best = (score, columns, heights)
    assert best is not None
    assert max(best[2]) <= max_height, ("brief columns", best[2], max_height)
    return best[1], best[2]


def draw_briefs(page):
    page.text(24, 641, "ALSO ON THURSDAY 26 NOVEMBER", "bold", 13, RED)
    column_width = 232
    columns, heights = brief_columns(column_width, 271)
    for column_index, column in enumerate(columns):
        left = 24 + column_index * 248
        cursor = 659
        if column_index:
            page.line([(left - 8, 659), (left - 8, 930)], RULE, 0.5)
        for story, lines, entry_height in column:
            for line_index, line in enumerate(lines):
                page.text(left, cursor + line_index * 11.5, line, "narrow", 11, RED if line_index == 0 else INK)
            cursor += entry_height
    page.line([(760, 641), (760, 930)], RULE, 0.5)
    draw_map(page, 773, 641, 227, 289)
    return heights


def draw_bottom(page):
    page.rect((24, 942, 1000, 980), PAPER, RED, 1)
    end = page.paragraph(33, 949, DATE_CHECK, 958, "body", 11, 12, max_lines=2, fill=RED)
    assert end <= 979
    page.paragraph(24, 988, FOOTER, 976, "narrow", 11, 12, max_lines=2, fill=MUTED)


def render(destination: Path):
    assert [story.number for story in STORIES] == list(range(1, 44))
    page = Page()
    draw_header(page)
    draw_lead(page)
    draw_grid(page)
    draw_numbers(page)
    heights = draw_briefs(page)
    draw_bottom(page)
    for index, (first, first_text) in enumerate(page.text_boxes):
        for second, second_text in page.text_boxes[index + 1:]:
            overlap_x = min(first[2], second[2]) - max(first[0], second[0])
            overlap_y = min(first[3], second[3]) - max(first[1], second[1])
            assert overlap_x <= 0.15 or overlap_y <= 0.15, ("Overlapping text", first_text, second_text, overlap_x, overlap_y)
    result = page.image.resize((SIZE, SIZE), Image.Resampling.LANCZOS)
    result.save(destination, format="PNG", optimize=True, compress_level=9)
    data = destination.read_bytes()
    assert len(data) <= 1048576, len(data)
    print(f"{destination}: 1024x1024; {len(data)} bytes; sha256 {hashlib.sha256(data).hexdigest()}")
    print("Region counts:", dict(Counter(story.region for story in STORIES)))
    print("Field counts:", {field: sum(story.field == field for story in STORIES) for field in FIELDS})
    print(f"{len(page.text_boxes)} text boxes; minimum font {page.minimum_size:g}px; brief column heights {heights}; no text overlaps")


def main():
    parser = argparse.ArgumentParser(description="Draw the fixed 26 November 2026 news brief, without network access.")
    parser.add_argument("--output", type=Path, default=ROOT / "entry.png")
    arguments = parser.parse_args()
    render(arguments.output)


if __name__ == "__main__":
    main()
