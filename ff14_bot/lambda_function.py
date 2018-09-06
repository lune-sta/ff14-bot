import requests
import bs4
import dictdiffer
import slackweb

import config
from model.character import CharacterModel


def _to_i(val):
    try:
        val = int(val)
    except ValueError:
        val = 0
    return val


def _fetch_character_levels(character_id: int) -> dict:
    url = 'https://jp.finalfantasyxiv.com/lodestone/character/' \
          + str(character_id) + '/'

    page = requests.get(url).text
    soup = bs4.BeautifulSoup(page, 'html.parser')
    level = soup.select('div.character__level__list li')
    out = {}

    for x in level:
        out[x.find('img')['data-tooltip']] = _to_i(x.text)

    return out


def _get_character_levels_diff_list(character_id: int, user_name: str) -> list:
    levels = _fetch_character_levels(character_id)

    try:
        saved = CharacterModel.get(hash_key=character_id)
        diff = list(dictdiffer.diff(saved.levels, levels))
        saved.levels = levels
        saved.save()
        return diff

    except CharacterModel.DoesNotExist:
        save = CharacterModel(hash_key=character_id)
        save.name = user_name
        save.levels = levels
        save.save()


def lambda_handler(event, context):

    text = '★☆★ 昨日の進捗\n'

    if not CharacterModel.exists():
        CharacterModel.create_table(read_capacity_units=1, write_capacity_units=1)

    for chara in config.CHARACTERS:
        text = text + '■ ' + chara['name'] + '\n'
        diff_list = _get_character_levels_diff_list(chara['id'], chara['name'])
        for diff in diff_list:
            if diff[0] == 'change':
                text = text + '- ' + diff[1] + ': ' + str(diff[2][0]) + ' -> ' + str(diff[2][1]) + '\n'
        if len(diff_list) == 0:
            text = text + 'なし\n'

    slack = slackweb.Slack(url=config.SLACK_URL)
    slack.notify(text=text)


if __name__ == '__main__':
    lambda_handler({}, {})
