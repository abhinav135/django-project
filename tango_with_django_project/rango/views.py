from django.shortcuts import render
from rango.models import Category
from rango.models import Page
from rango.forms import CategoryForm
from rango.forms import UserForm, UserProfileForm
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from datetime import datetime
from rango.bing_search import run_query

def index(request):
# Query the database for a list of ALL categories currently stored.
#  Order the categories by no. likes in descending order.
#  Retrieve the top 5 only - or all if less than 5.
#  Place the list in our context_dict dictionary
#  that will be passed to the template engine.
    request.session.set_test_cookie()
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    context_dict = {'categories': category_list,'pages':page_list}
# Render the response and send it back!
    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']
    response = render(request, 'rango/index.html', context_dict)
    return response


def about(request):
    if request.session.test_cookie_worked():
        print("TEST COOKIE WORKED!")
        request.session.delete_test_cookie()

    context_dict = dict()
    context_dict['visits'] = request.session['visits']
    return render(request, 'rango/about.html',context_dict)

def show_category(request, category_name_slug):
# Create a context dictionary which we can pass
#  to the template rendering engine.
    context_dict = {}
    context_dict['result_list'] = None
    context_dict['query'] = None

    if request.method == 'POST':
        query = request.POST.get('query').strip()

        if query:
            result_list = run_query(query)
        context_dict['result_list'] = result_list
        context_dict['query'] = query
    try:
# Can we find a categoryname slug with the given name?
#  If we can't, the .get() method raises a DoesNotExist exception.
#  So the .get() method returns one model instance or raises an exception.
        category = Category.objects.get(slug=category_name_slug)
# Retrieve all of the associated pages.
#  Note that filter() will return a list of page objects or an empty list
        pages = Page.objects.filter(category=category).order_by('-views')

# Adds our results list to the template context under name pages.
        context_dict['pages'] = pages
# We also add the category object from
#  the database to the context dictionary.
#  We'll use this in the template to verify that the category exists.
        context_dict['category'] = category
    except Category.DoesNotExist:
# We get here if we didn't find the specified category.
#  Don't do anything
# the template will display the "no category" message for us.
        context_dict['category'] = None
        context_dict['pages'] = None
# Go render the response and return it to the client.
    return render(request, 'rango/category.html', context_dict)

def add_category(request):
    form = CategoryForm()
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return index(request)
        else:
            print(form.errors)
    return render(request, 'rango/add_category.html', {'form': form})


from rango.forms import PageForm
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None
    form = PageForm()
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                return show_category(request, category_name_slug)
        else:
            print(form.errors)
    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context_dict)

def register(request):
# A boolean value for telling the template
#  whether the registration was successful.
#  Set to False initially. Code changes value to
#  True when registration succeeds.
    registered = False
# If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
# Attempt to grab information from the raw form information.
#  Note that we make use of both UserForm and UserProfileForm.
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)
# If the two forms are valid...
        if user_form.is_valid() and profile_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save()
# Now we hash the password with the set_password method.
#  Once hashed, we can update the user object.
            user.set_password(user.password)
            user.save()
# Now sort out the UserProfile instance.
#  Since we need to set the user attribute ourselves,
#  we set commit=False. This delays saving the model
#  until we're ready to avoid integrity problems.
            profile = profile_form.save(commit=False)
            profile.user = user
# Did the user provide a profile picture?
#  If so, we need to get it from the input form and
# put it in the UserProfile model.
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            profile.save()
                # Update our variable to indicate that the template
                #  registration was successful.
            registered = True
        else:
            # Invalid form or forms - mistakes or something else?
        #  Print problems to the terminal.
            print(user_form.errors, profile_form.errors)
    else:
        # Not a HTTP POST, so we render our form using two ModelForm instances.
        #  These forms will be blank, ready for user input.
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request, 'rango/register.html',{'user_form': user_form, 'profile_form': profile_form, 'registered': registered})

def user_login(request):
# If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
# Gather the username and password provided by the user.
#  This information is obtained from the login form.
#  We use request.POST.get('<variable>') as opposed
#  to request.POST['<variable>'], because the
#  request.POST.get('<variable>') returns None if the
#  value does not exist, while request.POST['<variable>']
#  will raise a KeyError exception.
        username = request.POST.get('username')
        password = request.POST.get('password')
# Use Django's machinery to attempt to see if the username/password
#  combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)
# If we have a User object, the details are correct.
#  If None (Python's way of representing the absence of a value), no user
#  with matching credentials was found.
        if user:
#  Is the account active? It could have been disabled.
            if user.is_active:
# If the account is valid and active, we can log the user in.
#  We'll send the user back to the homepage.
                login(request, user)
                return HttpResponseRedirect(reverse('index'))
            else:
# An inactive account was used - no logging in!
                return HttpResponse("Your Rango account is disabled.")
        else:
# Bad login details were provided. So we can't log the user in.
            print("Invalid login details: {0}, {1}".format(username, password))
            return HttpResponse("Invalid login details supplied.")
# The request is not a HTTP POST, so display the login form.
#  This scenario would most likely be a HTTP GET.
    else:
# No context variables to pass to the template system, hence the
#  blank dictionary object...
        return render(request, 'rango/login.html', {})

@login_required
def restricted(request):
    return HttpResponse("Since you're logged in, you can see this text!")

@login_required
def user_logout(request):
# Since we know the user is logged in, we can now just log them out.
    logout(request)
# Take the user back to the homepage.
    return HttpResponseRedirect(reverse('index'))

def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, 'visits', '1'))
    last_visit_cookie = get_server_side_cookie(request, 'last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')
    if (datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        # update the last visit cookie now that we have updated the count
        request.session['last_visit'] = str(datetime.now())
    else: # set the last visit cookie
        request.session['last_visit'] = last_visit_cookie
    request.session['visits'] = visits


def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val

def search(request):
    result_list = []
    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query: # Run our Bing function to get the results list!
            result_list = run_query(query)
    return render(request, 'rango/category.html', {'result_list': result_list})

from django.shortcuts import redirect
def track_url(request):
    page_id = None
    url = '/rango/'
    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']
            try:
                page = Page.objects.get(id=page_id)
                page.views = page.views + 1
                page.save()
                url = page.url
            except:
                pass
    return redirect(url)


from django.contrib.auth.decorators import login_required
@login_required
def like_category(request):
    cat_id = None
    if request.method == 'GET':
        cat_id = request.GET['category_id']
    likes = 0
    if cat_id:
        cat = Category.objects.get(id=int(cat_id))
        if cat:
            likes = cat.likes + 1
            cat.likes = likes
            cat.save()
    return HttpResponse(likes)

def get_category_list(max_results=0, starts_with=''):
    cat_list = []
    if starts_with:
        cat_list = Category.objects.filter(name__istartswith=starts_with)
    if max_results > 0:
        if len(cat_list) > max_results:
            cat_list = cat_list[:max_results]
    return cat_list

def suggest_category(request):
    cat_list = []
    starts_with = ''
    if request.method == 'GET':
        starts_with = request.GET['suggestion']
    cat_list = get_category_list(8, starts_with)
    return render(request, 'rango/cats.html', {'cats': cat_list})

@login_required
def auto_add_page(request):
    cat_id = request.GET['category_id']
    print("here", cat_id)

    cat = Category.objects.get(slug=(cat_id))
    if request.method == 'GET':
        title = (request.GET['page_name'])
        url = request.GET['page_url']
        page = Page()
        page.category = cat
        page.title = title
        page.url = url
        page.views = 0
        page.save()

    return HttpResponseRedirect(reverse('category'))
