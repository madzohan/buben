from flask import current_app

from api.crawlers.google_docs import \
    bp as docs_bp,\
    parse as docs_parse


@docs_bp.cli.command("parse")
def docs_parse_cmd():
    """
    Parse Google Docs pages and populate Product & Review data
    """
    # initialize database connection and perform migrations (as needed)
    from api.models import db, ma, migrate
    db.init_app(current_app)
    ma.init_app(current_app)
    migrate.init_app(current_app, db)

    # call actual docs parser
    docs_parse(db)
