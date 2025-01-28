import hashlib

# generates unique id by hashing user's discord id
def generate_unique_id(discord_user_id):
    id = f"{discord_user_id}".encode('utf-8')
    hashed_id = hashlib.sha256(id).hexdigest()
    return hashed_id