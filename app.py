import json, os, hashlib
from flask import Flask, render_template, request, redirect, session, url_for

app = Flask(__name__)
app.secret_key = 'under1000-nairobi-key'

# ── DATA PERSISTENCE ──────────────────────────────────────────────────────
def load_json(name):
    path = f'{name}.json'
    if not os.path.exists(path): return []
    with open(path, 'r', encoding='utf-8') as f: return json.load(f)

def save_json(name, data):
    with open(f'{name}.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def hash_pw(pw): return hashlib.sha256(pw.encode()).hexdigest()

ADMINS = {
    'chief_admin':    {'password': 'chief123',    'role': 'Chief Admin',         'icon': 'crown',   'desc': 'Full access — manage everything'},
    'listings_admin': {'password': 'listings123', 'role': 'Listings Manager',    'icon': 'package', 'desc': 'Approve & reject product listings'},
    'sellers_admin':  {'password': 'sellers123',  'role': 'Sellers Manager',     'icon': 'users',   'desc': 'Manage seller accounts & disputes'},
    'content_admin':  {'password': 'content123',  'role': 'Content Moderator',   'icon': 'shield',  'desc': 'Review images & descriptions'},
    'reports_admin':  {'password': 'reports123',  'role': 'Reports & Analytics', 'icon': 'chart',   'desc': 'View stats & generate reports'},
}

PRICE_RANGES = [(0, 100), (101, 200), (201, 300), (301, 400), (401, 500), (501, 600), (601, 700), (701, 800), (801, 900), (901, 1000)]

# ── SVG ICON LIBRARY ──────────────────────────────────────────────────────
def icon(name, size=16, cls=''):
    icons = {
        'map-pin':   '<path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>',
        'store':     '<path d="M2 7l1-4h18l1 4"/><path d="M22 7v13a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V7"/><path d="M12 7v14"/><path d="M2 7h20"/>',
        'whatsapp':  '<path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347z"/><path d="M12 2C6.477 2 2 6.477 2 12c0 1.89.525 3.66 1.438 5.168L2 22l4.832-1.438A9.96 9.96 0 0 0 12 22c5.523 0 10-4.477 10-10S17.523 2 12 2z"/>',
        'instagram': '<rect x="2" y="2" width="20" height="20" rx="5" ry="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1.5" fill="currentColor"/>',
        'tiktok':    '<path d="M19.321 5.562a5.122 5.122 0 0 1-.443-.258 6.228 6.228 0 0 1-1.138-.966c-.849-.971-1.166-1.956-1.282-2.338h.004C16.381 1.773 16.4 1.5 16.4 1.5h-3.697v13.9c0 .185 0 .368-.007.548v.038a2.697 2.697 0 0 1-2.692 2.514 2.697 2.697 0 0 1-2.697-2.697 2.697 2.697 0 0 1 2.697-2.697c.264 0 .517.038.757.107V9.49a6.393 6.393 0 0 0-.757-.045 6.394 6.394 0 0 0-6.394 6.394 6.394 6.394 0 0 0 6.394 6.394 6.394 6.394 0 0 0 6.394-6.394V8.408a9.76 9.76 0 0 0 5.7 1.819V6.534a5.833 5.833 0 0 1-2.777-.972z"/>',
        'crown':     '<path d="M2 20h20"/><path d="m3 9 4 2 5-7 5 7 4-2-2 9H5L3 9z"/>',
        'package':   '<path d="M12 2l9 4.5v11L12 22l-9-4.5v-11L12 2z"/><path d="M12 2v20"/><path d="M3 6.5l9 4.5 9-4.5"/>',
        'users':     '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
        'shield':    '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
        'chart':     '<line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>',
        'user':      '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
        'log-out':   '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/>',
        'tag':       '<path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/>',
        'check':     '<polyline points="20 6 9 17 4 12"/>',
        'x':         '<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>',
        'plus':      '<line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>',
        'grid':      '<rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/>',
        'lock':      '<rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
        'mail':      '<path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/>',
        'arrow-r':   '<line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>',
        'filter':    '<polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/>',
        'trending':  '<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/>',
        'clock':     '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
        'eye':       '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>',
        'bell':      '<path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/>',
        'settings':  '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>',
    }
    stroke = 'none' if name in ('instagram','tiktok','whatsapp') else 'currentColor'
    fill   = 'currentColor' if name in ('instagram','tiktok','whatsapp') else 'none'
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="{fill}" stroke="{stroke}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon {cls}">{icons.get(name,"")}</svg>'

def admin_icon(name, size=28):
    return icon(name, size=size, cls='admin-role-icon')

NOTE_SVG = """<svg width="82" height="44" viewBox="0 0 82 44" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="ng" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#0a4a3a"/><stop offset="50%" style="stop-color:#0d5c48"/><stop offset="100%" style="stop-color:#083d30"/>
    </linearGradient>
    <linearGradient id="gs" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#ffd700"/><stop offset="50%" style="stop-color:#c8a86b"/><stop offset="100%" style="stop-color:#ffd700"/>
    </linearGradient>
    <pattern id="mt" x="0" y="0" width="5" height="5" patternUnits="userSpaceOnUse">
      <text x="0" y="4" font-size="2.5" fill="#1a6e56" font-family="monospace" opacity="0.4">K</text>
    </pattern>
  </defs>
  <rect width="82" height="44" fill="url(#ng)" rx="3"/>
  <rect width="82" height="44" fill="url(#mt)"/>
  <rect x="0" y="0" width="82" height="15" fill="#87CEEB" opacity="0.07"/>
  <text x="41" y="5.5" font-size="2.4" fill="#4dcca0" font-family="serif" text-anchor="middle" letter-spacing="0.4" opacity="0.85">CENTRAL BANK OF KENYA</text>
  <rect x="34" y="7" width="5" height="23" fill="#1a7a60" opacity="0.9"/>
  <ellipse cx="36.5" cy="7" rx="6" ry="3" fill="#1a7a60" opacity="0.9"/>
  <ellipse cx="36.5" cy="5.5" rx="4" ry="2" fill="#2a9a7a" opacity="0.85"/>
  <rect x="36" y="1" width="1.2" height="6" fill="#2aaa8a"/>
  <rect x="25" y="27" width="23" height="5" fill="#1a7a60" opacity="0.85"/>
  <rect x="21" y="31" width="31" height="4" fill="#156050" opacity="0.9"/>
  <rect x="35" y="11" width="2.5" height="1.8" fill="#87CEEB" opacity="0.55"/>
  <rect x="35" y="15" width="2.5" height="1.8" fill="#87CEEB" opacity="0.55"/>
  <rect x="35" y="19" width="2.5" height="1.8" fill="#87CEEB" opacity="0.5"/>
  <rect x="26" y="23" width="5" height="7" fill="#1a7a60" opacity="0.7"/>
  <rect x="43" y="23" width="5" height="7" fill="#1a7a60" opacity="0.7"/>
  <rect x="0" y="35" width="82" height="9" fill="#083d30"/>
  <text x="3" y="41" font-size="2.5" fill="#2aaa8a" font-family="monospace" opacity="0.65">AA 0000001</text>
  <path d="M9,12 Q12,7.5 16,10.5 Q13,11.5 14,14.5 Q10,13.5 9,12Z" fill="#2aaa8a" opacity="0.55"/>
  <ellipse cx="69" cy="27" rx="6" ry="5" fill="#1a7a60" opacity="0.85"/>
  <ellipse cx="72" cy="23" rx="3.5" ry="3" fill="#1a7a60" opacity="0.85"/>
  <path d="M74.5,24 Q78,25.5 77,29 Q76,30.5 74.5,29" stroke="#1a7a60" stroke-width="1.5" fill="none" opacity="0.85"/>
  <ellipse cx="68" cy="22.5" rx="2.5" ry="3" fill="#156050" opacity="0.7"/>
  <circle cx="73" cy="22" r="0.5" fill="#87CEEB" opacity="0.8"/>
  <path d="M73.5,25 Q75.5,27 74,28" stroke="#c8a86b" stroke-width="0.8" fill="none" opacity="0.7"/>
  <rect x="64" y="31" width="2" height="4" rx="0.5" fill="#156050" opacity="0.8"/>
  <rect x="67" y="31" width="2" height="4" rx="0.5" fill="#156050" opacity="0.8"/>
  <rect x="70" y="31" width="2" height="4" rx="0.5" fill="#156050" opacity="0.8"/>
  <rect x="73" y="31" width="2" height="4" rx="0.5" fill="#156050" opacity="0.8"/>
  <rect x="19" y="0" width="2" height="44" fill="url(#gs)" opacity="0.45"/>
  <rect x="1" y="1" width="80" height="42" fill="none" stroke="#2aaa8a" stroke-width="0.6" opacity="0.35" rx="2"/>
</svg>"""

@app.context_processor
def inject_globals():
    return {
        'icon': icon,
        'admin_icon': admin_icon,
        'note_svg': NOTE_SVG,
        'admins': ADMINS,
        'price_ranges': PRICE_RANGES,
        'categories': ['Tops','Dresses','Pants','Skirts','Jackets','Shoes','Hats','Accessories','Other']
    }

# ── ROUTES ────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    products = [p for p in load_json('products') if p.get('approved')]
    return render_template('main.html', view='shop', products=products)

@app.route('/register', methods=['GET','POST'])
def register():
    fe=None
    if request.method=='POST':
        u, e, p = request.form['username'].strip(), request.form['email'].strip(), request.form['password']
        users = load_json('users')
        if any(x['username'] == u or x['email'] == e for x in users):
            fe='Username or email already taken.'
        else:
            users.append({'id': len(users)+1, 'username': u, 'email': e, 'password': hash_pw(p), 'created_at': '2025-01-01'})
            save_json('users', users)
            session['buyer'] = u; return redirect('/')
    return render_template('main.html', view='auth', mode='register', auth_title='Create Account', auth_subtitle='Join Under 1000 for free', btn_cls='f', btn_text='Register', btn_icon='arrow-r', flash_err=fe)

@app.route('/login', methods=['GET','POST'])
def login():
    fe=None
    if request.method=='POST':
        u, p = request.form['username'].strip(), request.form['password']
        users = load_json('users')
        if any(x['username'] == u and x['password'] == hash_pw(p) for x in users):
            session['buyer'] = u; return redirect('/')
        fe='Wrong username or password.'
    return render_template('main.html', view='auth', mode='login', auth_title='Welcome Back', auth_subtitle='Log in to your account', btn_cls='t', btn_text='Log in', btn_icon='arrow-r', flash_err=fe)

@app.route('/admin/login', methods=['GET','POST'])
def admin_login():
    fe=None
    if request.method=='POST':
        u, p = request.form['username'].strip(), request.form['password']
        if u in ADMINS and ADMINS[u]['password'] == p:
            session['admin'] = u; return redirect('/admin')
        fe='Invalid admin credentials.'
    return render_template('main.html', view='auth', mode='admin_login', auth_title='Admin Access', auth_subtitle='Enter credentials', btn_cls='g', btn_text='Enter Dashboard', btn_icon='settings', flash_err=fe)

@app.route('/logout')
def logout():
    session.clear(); return redirect('/')

@app.route('/sell', methods=['GET','POST'])
def sell():
    if not session.get('buyer') and not session.get('admin'): return redirect('/login')
    fe=fo=None
    if request.method=='POST':
        try:
            price = int(request.form.get('price', 0))
            if price > 1000: fe='Max price is 1000.'
            else:
                products = load_json('products')
                products.append({
                    'id': len(products)+1,
                    'name': request.form['name'],
                    'price': price,
                    'seller': request.form['seller'],
                    'whatsapp': request.form['whatsapp'],
                    'instagram': request.form.get('instagram', ''),
                    'tiktok': request.form.get('tiktok', ''),
                    'location': request.form['location'],
                    'image_url': request.form.get('image_url', ''),
                    'category': request.form.get('category', 'Other'),
                    'approved': 0,
                    'submitted_by': session.get('buyer') or session.get('admin')
                })
                save_json('products', products)
                fo='Listing submitted for approval!'
        except: fe='Error processing form.'
    return render_template('main.html', view='sell', flash_err=fe, flash_ok=fo)

@app.route('/admin')
def admin():
    if not session.get('admin'): return redirect('/admin/login')
    tab = request.args.get('tab', 'listings')
    products = load_json('products')
    buyers = load_json('users')
    stats = {
        'total': len(products),
        'pending': len([p for p in products if not p.get('approved')]),
        'live': len([p for p in products if p.get('approved')]),
        'buyers': len(buyers)
    }
    stats_items = [
        {'val': stats['total'], 'label': 'Total', 'icon': 'package', 'color': 'var(--terra)'},
        {'val': stats['pending'], 'label': 'Pending', 'icon': 'clock', 'color': 'var(--gold)'},
        {'val': stats['live'], 'label': 'Live', 'icon': 'trending', 'color': 'var(--forest)'},
        {'val': stats['buyers'], 'label': 'Buyers', 'icon': 'users', 'color': 'var(--forest)'}
    ]
    return render_template('main.html', view='admin', admin_info=ADMINS[session['admin']], tab=tab, 
                           admin_products=sorted(products, key=lambda x: (x.get('approved',0), -x.get('id',0))), 
                           admin_buyers=buyers[::-1], stats_items=stats_items)

@app.route('/admin/approve/<int:pid>', methods=['POST'])
def approve(pid):
    if not session.get('admin'): return redirect('/admin/login')
    products = load_json('products')
    for p in products:
        if p['id'] == pid: 
            p['approved'] = 1; break
    save_json('products', products)
    return redirect('/admin?tab=listings')

@app.route('/admin/delete/<int:pid>', methods=['POST'])
def delete(pid):
    if not session.get('admin'): return redirect('/admin/login')
    products = load_json('products')
    products = [p for p in products if p['id'] != pid]
    save_json('products', products)
    return redirect('/admin?tab=listings')

if __name__ == '__main__':
    app.run(debug=True)
