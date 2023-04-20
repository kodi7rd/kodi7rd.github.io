from . import SubtitleAPI

sub = SubtitleAPI('english', 'farsi/persian')
sub.movie(title='Pi', release_type='bluray').download().extract()

#def movie(self, title=None, year=None, imdb_id=None, release_type=None):
#subscene.movie(title='Tenet',year=2020,release_type='bluray')
#result = subscene.movie(title='Finch',year=2021)

#def tvshow(self, title=None, imdb_id=None, release_type=None, season=None, episode=None):
result = subscene.tvshow(title='The 100',season=1, episode=3)