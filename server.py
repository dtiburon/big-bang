#!/usr/bin/env python
from bigbang import app
import config

if __name__ == "__main__":
    app.config['SITE_DOMAIN'] = config.SITE_DOMAIN
    app.run(debug=True)