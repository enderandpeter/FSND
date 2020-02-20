# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json

from sqlalchemy import text

import config
import dateutil.parser
from datetime import timezone
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects import postgresql
import logging
from logging import Formatter, FileHandler
from flask_wtf.csrf import CSRFProtect
from forms import *
import sys

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
csrf = CSRFProtect(app)

migrate = Migrate(app, db)


# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#

class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'))
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'))
    show_at = db.Column(db.DateTime(timezone=True), nullable=True)
    venue = db.relationship("Venue", backref="shows")
    artist = db.relationship("Artist", backref="shows")


class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, server_default='0')
    website = db.Column(db.String(500))
    genres = db.Column(postgresql.ARRAY(db.String))
    seeking_description = db.Column(db.String(500))
    show_props = [
            'id',
            'name',
            'city',
            'state',
            'address',
            'phone',
            'genres',
            'seeking_talent',
            'seeking_description',
            'website',
            'image_link',
            'facebook_link'
        ]


class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(postgresql.ARRAY(db.String))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean, server_default='0')
    seeking_description = db.Column(db.String(500))
    show_props = [
        'id',
        'name',
        'genres',
        'city',
        'state',
        'phone',
        'website',
        'image_link',
        'facebook_link',
        'seeking_venue',
        'seeking_description',
    ]

# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    error = False
    data = []
    try:
        venue_rows = Venue.query.order_by(text("concat(city, ', ', state)")).all()
        row = {
            'city': '',
            'state': '',
            'venues': []
        }
        for venue in venue_rows:
            if not (venue.city == row['city'] and venue.state == row['state']):
                if len(row['city']) > 0:
                    data.append(row)

                row = {
                    'city': venue.city,
                    'state': venue.state,
                    'venues': []
                }

            row['venues'].append({
                'id': venue.id,
                'name': venue.name
            })

        data.append(row)
    except:
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        flash('There was an error retrieving the venues')
        return redirect(url_for('create_venue_form'))

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    response = {
        "count": 1,
        "data": [{
            "id": 2,
            "name": "The Dueling Pianos Bar",
            "num_upcoming_shows": 0,
        }]
    }
    return render_template('pages/search_venues.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    error = False
    data = {}
    try:
        venue = Venue.query.get(venue_id)
        data = {prop: getattr(venue, prop) for prop in venue.show_props}

        if len(venue.shows) == 0:
            data['past_shows'] = []
            data['upcoming_shows'] = []
        else:
            data['past_shows'] = [
                {
                    "artist_id": show.artist_id,
                    "artist_name": show.artist.name,
                    "artist_image_link": show.artist.image_link,
                    "show_at": show.show_at.isoformat()
                } for show in venue.shows if show.show_at < datetime.now(timezone.utc)
            ]

            data['upcoming_shows'] = [
                {
                    "artist_id": show.artist_id,
                    "artist_name": show.artist.name,
                    "artist_image_link": show.artist.image_link,
                    "show_at": show.show_at.isoformat()
                } for show in venue.shows if show.show_at >= datetime.now(timezone.utc)
            ]

        data['past_shows_count'] = len(data['past_shows'])
        data['upcoming_shows_count'] = len(data['upcoming_shows'])
        data['edit_url'] = url_for('edit_venue', **{'venue_id': venue_id})
    except:
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        flash(f'Could not find venue with id {venue_id}')
        return redirect(url_for('venues'))

    return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm()

    if not form.validate_on_submit():
        for category, errors in form.errors.items():
            for error in errors:
                flash(error, form[category].label)
        return redirect(url_for('create_venue_form'))

    venue_props = Venue.show_props
    venue_props.remove('id')

    error = False
    try:
        venue_data = {venue_prop: form.data[venue_prop] for venue_prop in venue_props}
        venue = Venue(**venue_data)
        db.session.add(venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        flash('There was an error saving the venue')
        return redirect(url_for('create_venue_form'))

    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return 'No denyin'


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    error = False
    data = []
    try:
        artists = Artist.query.all()
        for artist in artists:
            data.append({
                "id": artist.id,
                "name": artist.name
            })
    except:
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        flash('There was an error retrieving the artists')
        return redirect(url_for('create_artist_form'))

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # search for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    response = {
        "count": 1,
        "data": [{
            "id": 4,
            "name": "Guns N Petals",
            "num_upcoming_shows": 0,
        }]
    }
    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page

    error = False
    data = {}
    try:
        artist = Artist.query.get(artist_id)
        data = {prop: getattr(artist, prop) for prop in artist.show_props}

        if len(artist.shows) == 0:
            data['past_shows'] = []
            data['upcoming_shows'] = []

        else:
            data['past_shows'] = [
                {
                    "venue_id": show.venue_id,
                    "venue_name": show.venue.name,
                    "venue_image_link": show.venue.image_link,
                    "show_at": show.show_at.isoformat()
                } for show in artist.shows if show.show_at < datetime.now(timezone.utc)
            ]

            data['upcoming_shows'] = [
                {
                    "venue_id": show.venue_id,
                    "venue_name": show.venue.name,
                    "venue_image_link": show.venue.image_link,
                    "show_at": show.show_at.isoformat()
                } for show in artist.shows if show.show_at >= datetime.now(timezone.utc)
            ]
        data['past_shows_count'] = len(data['past_shows'])
        data['upcoming_shows_count'] = len(data['upcoming_shows'])
        data['edit_url'] = url_for('edit_artist', **{'artist_id': artist_id})
    except:
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        flash(f'Could not find artist with id {artist_id}')
        return redirect(url_for('artists'))

    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    error = False
    artist_form_data = {}
    artist = None

    try:
        artist = Artist.query.get(artist_id)
        artist_props = artist.show_props[:]
        try:
            artist_props.remove('id')
        except ValueError:
            pass

        artist_form_data = {prop: getattr(artist, prop) for prop in artist_props}
    except:
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()

    form = ArtistForm(data=artist_form_data)
    artist_page_data = {
        'id': artist.id,
        'name': artist.name
    }
    return render_template('forms/edit_artist.html', form=form, artist=artist_page_data)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    form = ArtistForm()

    if not form.validate_on_submit():
        for category, errors in form.errors.items():
            for error in errors:
                flash(error, form[category].label)
        return redirect(url_for('edit_artist'))

    error = False
    try:
        venue = Artist.query.get(artist_id)
        venue_props = venue.show_props[:]
        venue_props.remove('id')
        for venue_prop in venue_props:
            setattr(venue, venue_prop, form.data[venue_prop])

        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        flash('There was an error saving the artist')
        return redirect(url_for('edit_artist', **{'artist_id': artist_id}))

    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was saved!')

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    error = False
    venue_form_data = {}
    venue = None

    try:
        venue = Venue.query.get(venue_id)
        venue_props = venue.show_props[:]
        venue_props.remove('id')

        venue_form_data = {prop: getattr(venue, prop) for prop in venue_props}
    except:
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()

    form = VenueForm(data=venue_form_data)

    venue_page_data = {
        'id': venue.id,
        'name': venue.name
    }
    return render_template('forms/edit_venue.html', form=form, venue=venue_page_data)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    form = VenueForm()

    if not form.validate_on_submit():
        for category, errors in form.errors.items():
            for error in errors:
                flash(error, form[category].label)
        return redirect(url_for('edit_venue'))

    error = False
    try:
        venue = Venue.query.get(venue_id)
        venue_props = venue.show_props[:]
        venue_props.remove('id')
        for venue_prop in venue_props:
            setattr(venue, venue_prop, form.data[venue_prop])

        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        flash('There was an error saving the venue')
        return redirect(url_for('edit_venue', **{'venue_id': venue_id}))

    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was saved!')
    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form

    form = ArtistForm()

    if not form.validate_on_submit():
        for category, errors in form.errors.items():
            for error in errors:
                flash(error, form[category].label)
        return redirect(url_for('create_artist_form'))

    artist_props = Artist.show_props
    artist_props.remove('id')

    error = False
    try:
        artist_data = {artist_prop: form.data[artist_prop] for artist_prop in artist_props}
        artist = Artist(**artist_data)
        db.session.add(artist)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        flash('There was an error saving the artist')
        return redirect(url_for('create_artist_form'))

    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    data = []
    show_list = Show.query.all()
    for show in show_list:
        venue = Venue.query.get(show.venue_id)
        artist = Artist.query.get(show.artist_id)
        show_data = {
            'venue_id': show.venue_id,
            'venue_name': venue.name,
            'artist_id': artist.id,
            'artist_name': artist.name,
            'artist_image_link': artist.image_link,
            'show_at': show.show_at.isoformat()
        }
        data.append(show_data)

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    form = ShowForm()

    if not form.validate_on_submit():
        for category, errors in form.errors.items():
            for error in errors:
                flash(error, form[category].label)
        return redirect(url_for('create_shows'))

    show_props = ['artist_id', 'venue_id', 'show_at']
    error = False
    try:
        show_data = {show_prop: form.data[show_prop] for show_prop in show_props}
        show = Show(**show_data)
        db.session.add(show)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        flash('There was an error saving the show')
        return redirect(url_for('create_shows'))

    # on successful db insert, flash success
    flash('Show was successfully listed!')
    return redirect(url_for('index'))


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
