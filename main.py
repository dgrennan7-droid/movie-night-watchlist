"""Movie Night Watchlist: a simple fun Drafter site.

Add movies with a genre and star rating, mark them as watched, remove them,
and see stats like your average rating and top movie.

Routes that only show pages are not unit tested directly; the helper
functions they rely on are unit tested instead.
"""
from dataclasses import dataclass

from drafter import *

set_site_information(author="Daniel Grennan",\n description="Plan your movie night with ease!",\n sources="Assisted by LLMs",\n planning="part0.pdf and part1,pdf",\n links=[]
GENRES = ["Action", "Comedy", "Horror", "Sci-Fi", "Romance"]
RATINGS = ["1", "2", "3", "4", "5"]
MAX_MOVIES = 12


# ---------------------------------------------------------------- dataclasses
@dataclass
class Movie:
    """One movie on the watchlist."""
    title: str
    genre: str
    rating: int  # 1 to 5 stars
    watched: bool


@dataclass
class State:
    """Everything the website remembers between pages."""
    owner_name: str
    watchlist: list[Movie]
    movies_watched: int
    status_message: str


# ------------------------------------------------------------ helper functions
def average_rating(movies: list[Movie]) -> float:
    """Return the average star rating (0.0 if there are no movies)."""
    if len(movies) == 0:
        return 0.0
    total = 0
    for movie in movies:
        total += movie.rating
    return total / len(movies)


def count_genre(movies: list[Movie], genre: str) -> int:
    """Count how many movies belong to the given genre."""
    count = 0
    for movie in movies:
        if movie.genre == genre:
            count += 1
    return count


def count_watched(movies: list[Movie]) -> int:
    """Count how many movies are marked watched."""
    count = 0
    for movie in movies:
        if movie.watched:
            count += 1
    return count


def find_movie(title: str, movies: list[Movie]) -> int:
    """Return the index of the movie with this title, or -1 if missing."""
    for index, movie in enumerate(movies):
        if movie.title.lower() == title.lower():
            return index
    return -1


def unwatched_titles(movies: list[Movie]) -> list[str]:
    """Return the titles of movies that are not watched yet."""
    titles = []
    for movie in movies:
        if not movie.watched:
            titles.append(movie.title)
    return titles


def all_titles(movies: list[Movie]) -> list[str]:
    """Return every movie title, in order."""
    titles = []
    for movie in movies:
        titles.append(movie.title)
    return titles


def top_movie(movies: list[Movie]) -> str:
    """Return the title with the highest rating ('' if no movies)."""
    best = ""
    best_rating = 0
    for movie in movies:
        if movie.rating > best_rating:
            best = movie.title
            best_rating = movie.rating
    return best


def stars(rating: int) -> str:
    """Turn a rating number into star characters."""
    return "★" * rating + "☆" * (5 - rating)


def genre_rows(movies: list[Movie]) -> list[list[str]]:
    """Build a table (header first) of how many movies are in each genre."""
    rows = [["Genre", "Movies"]]
    for genre in GENRES:
        rows.append([genre, str(count_genre(movies, genre))])
    return rows


# ---------------------------------------------------------------------- routes
@route
def index(state: State) -> Page:
    """Home page: greeting, status, and navigation buttons."""
    return Page(state, [
        Header("🎬 Movie Night Watchlist", 1),
        "Welcome, " + state.owner_name + "!",
        "Status: " + state.status_message,
        HorizontalRule(),
        "Movies on your list: " + str(len(state.watchlist)),
        "Movies watched: " + str(state.movies_watched),
        HorizontalRule(),
        Button("Change my name", name_page),
        Button("Add a movie", add_page),
        Button("See my list", list_page),
        Button("See my stats", stats_page),
        Button("Clear everything", reset_list),
    ])


@route
def name_page(state: State) -> Page:
    """Page for changing the owner's name."""
    return Page(state, [
        Header("What's your name?", 1),
        TextBox("owner_name", state.owner_name),
        Button("Save", save_name),
        Button("Back", index),
    ])


@route
def save_name(state: State, owner_name: str) -> Page:
    """Save the owner's name if it is not blank."""
    owner_name = owner_name.strip()
    if owner_name == "":
        state.status_message = "Name can't be blank."
        return name_page(state)
    state.owner_name = owner_name
    state.status_message = "Nice to meet you, " + owner_name + "!"
    return index(state)


@route
def add_page(state: State) -> Page:
    """Page with the add-movie form."""
    return Page(state, [
        Header("Add a Movie", 1),
        "Status: " + state.status_message,
        "Title:",
        TextBox("title", ""),
        "Genre:",
        SelectBox("genre", GENRES, GENRES[0]),
        "Your rating (1-5 stars):",
        SelectBox("rating", RATINGS, "3"),
        LineBreak(),
        Button("Add movie", add_movie),
        Button("Back", index),
    ])


@route
def add_movie(state: State, title: str, genre: str, rating: str) -> Page:
    """Validate the form and add a new Movie to the watchlist."""
    title = title.strip()
    if len(state.watchlist) >= MAX_MOVIES:
        state.status_message = "Your list is full (max " + str(MAX_MOVIES) + ")."
        return add_page(state)
    if title == "":
        state.status_message = "Please enter a title."
        return add_page(state)
    if find_movie(title, state.watchlist) != -1:
        state.status_message = title + " is already on your list."
        return add_page(state)
    state.watchlist.append(Movie(title, genre, int(rating), False))
    state.status_message = "Added " + title + "!"
    return list_page(state)


@route
def list_page(state: State) -> Page:
    """Page showing the watchlist with watched/remove controls."""
    content = [Header("My Watchlist", 1), "Status: " + state.status_message]
    if len(state.watchlist) == 0:
        content.append("Nothing here yet. Add a movie!")
    else:
        rows = [["Title", "Genre", "Rating", "Watched?"]]
        for movie in state.watchlist:
            watched_text = "Yes ✅" if movie.watched else "Not yet"
            rows.append([movie.title, movie.genre, stars(movie.rating),
                         watched_text])
        content.append(Table(rows))
        waiting = unwatched_titles(state.watchlist)
        if len(waiting) > 0:
            content.append("Mark as watched:")
            content.append(SelectBox("title_to_watch", waiting, waiting[0]))
            content.append(Button("Watched it!", mark_watched))
        everything = all_titles(state.watchlist)
        content.append("Remove a movie:")
        content.append(SelectBox("title_to_remove", everything, everything[0]))
        content.append(Button("Remove", remove_movie))
    content.append(Button("Add another", add_page))
    content.append(Button("Back", index))
    return Page(state, content)


@route
def mark_watched(state: State, title_to_watch: str) -> Page:
    """Mark the chosen movie as watched and update the watched count."""
    position = find_movie(title_to_watch, state.watchlist)
    if position == -1:
        state.status_message = "Couldn't find that movie."
    else:
        state.watchlist[position].watched = True
        state.movies_watched = count_watched(state.watchlist)
        state.status_message = "Enjoyed " + title_to_watch + "? 🍿"
    return list_page(state)


@route
def remove_movie(state: State, title_to_remove: str) -> Page:
    """Remove the chosen movie and update the watched count."""
    position = find_movie(title_to_remove, state.watchlist)
    if position == -1:
        state.status_message = "Couldn't find that movie."
    else:
        state.watchlist.pop(position)
        state.movies_watched = count_watched(state.watchlist)
        state.status_message = "Removed " + title_to_remove + "."
    return list_page(state)


@route
def stats_page(state: State) -> Page:
    """Stats page: average rating, top movie, and genre breakdown."""
    if len(state.watchlist) == 0:
        state.status_message = "Add some movies to see stats."
        return add_page(state)
    average = average_rating(state.watchlist)
    return Page(state, [
        Header("📊 Your Stats", 1),
        "Average rating: " + str(round(average, 2)) + " / 5",
        "Top rated: " + top_movie(state.watchlist),
        "Watched: " + str(state.movies_watched) + " of "
        + str(len(state.watchlist)),
        HorizontalRule(),
        Table(genre_rows(state.watchlist)),
        Button("Back", index),
    ])


@route
def reset_list(state: State) -> Page:
    """Clear the watchlist and reset the counters."""
    state.watchlist = []
    state.movies_watched = 0
    state.status_message = "List cleared."
    return index(state)


# ------------------------------------------------------------------ unit tests
SAMPLE = [Movie("Alien", "Horror", 5, True), Movie("Shrek", "Comedy", 4, False),
          Movie("Heat", "Action", 3, False)]

assert_equal(average_rating(SAMPLE), 4.0)
assert_equal(average_rating([]), 0.0)
assert_equal(count_genre(SAMPLE, "Horror"), 1)
assert_equal(count_genre(SAMPLE, "Romance"), 0)
assert_equal(count_watched(SAMPLE), 1)
assert_equal(find_movie("shrek", SAMPLE), 1)
assert_equal(find_movie("Nope", SAMPLE), -1)
assert_equal(unwatched_titles(SAMPLE), ["Shrek", "Heat"])
assert_equal(all_titles(SAMPLE), ["Alien", "Shrek", "Heat"])
assert_equal(top_movie(SAMPLE), "Alien")
assert_equal(top_movie([]), "")
assert_equal(stars(3), "★★★☆☆")
assert_equal(genre_rows(SAMPLE)[1], ["Action", "1"])

# ---------------------------------------------------------------- site settings
set_website_title("Movie Night Watchlist")
set_site_information(
    author="YOUR NAME HERE",
    description="Track movies, rate them, and see your watching stats.",
    sources=["Written by me with help from Claude (conversation uploaded)"],
    planning="planning.pdf",
    links=["https://github.com/YOUR-USERNAME/YOUR-REPO"]
)
hide_debug_information()

start_server(State("Movie Fan", [], 0, "Add your first movie!"))

