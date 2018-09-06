from pynamodb.models import Model
from pynamodb.attributes import NumberAttribute, UnicodeAttribute, JSONAttribute


class CharacterModel(Model):
    class Meta:
        table_name = 'ff14-character'
        region = 'us-west-2'

    c_id = NumberAttribute(hash_key=True)
    name = UnicodeAttribute()
    levels = JSONAttribute()
