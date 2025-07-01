# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from werkzeug.exceptions import NotFound

class PublicGuideController(http.Controller):

    @http.route([
        '/guide',
        '/guide/<string:main_slug>',
        '/guide/<string:main_slug>/<string:sub_slug>'
    ], type='http', auth='public', website=True)
    def render_guide_article(self, main_slug=None, sub_slug=None, **kwargs):
        domain = [('is_published', '=', True)]
        slug_to_find = sub_slug or main_slug
        if slug_to_find:
            domain.append(('slug', '=', slug_to_find))

        article = request.env['knowledge.article'].sudo().search(domain, limit=1) if slug_to_find else None
        if slug_to_find and not article:
            raise NotFound()

        top_articles = request.env['knowledge.article'].sudo().search([
            ('parent_id', '=', False),
            ('is_published', '=', True)
        ])

        sub_articles = request.env['knowledge.article'].sudo().search([
            ('parent_id', '=', article.id if article else False),
            ('is_published', '=', True)
        ])

        siblings = request.env['knowledge.article'].sudo().search([
            ('parent_id', '=', article.parent_id.id if article and article.parent_id else False),
            ('is_published', '=', True)
        ]) if article and article.parent_id else top_articles

        breadcrumbs = []
        current = article
        while current:
            breadcrumbs.insert(0, current)
            current = current.parent_id

        search_query = kwargs.get('q', '').strip()
        search_results = []
        if search_query:
            search_results = request.env['knowledge.article'].sudo().search([
                ('is_published', '=', True),
                ('name', 'ilike', search_query)
            ], limit=20)

        return request.render('public_knowledge_guide.public_guide_template', {
            'article': article,
            'top_articles': top_articles,
            'siblings': siblings,
            'sub_articles': sub_articles,
            'breadcrumbs': breadcrumbs,
            'search_query': search_query,
            'search_results': search_results,
        })
