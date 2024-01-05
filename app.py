from flask import Flask, render_template, request
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

app = Flask(__name__)


# Load your CSV data
columns = ['cid','year','year_order','first_name','last_name','season_win','season_loss','playoff_win','playoff_loss','tid']
df = pd.read_csv('coaches_season.csv',names = columns) 
df['season_games'] = df['season_win'] + df['season_loss']
df['playoff_games'] = df['playoff_win'] + df['playoff_loss']
df['total_games'] = df['season_games'] + df['playoff_games']
df['total_wins'] = df['season_win'] + df['playoff_win']
df['full_name'] = df['first_name'] + df['last_name']  

years = sorted(df['year'].unique())
teams = df['tid'].unique()

# Define a route to render the HTML page
@app.route('/', methods=['GET','POST'])
def home():
    teams_grouped_by_coach = df.groupby('cid')['tid'].unique().reset_index()

    fig_3 =  px.histogram(teams_grouped_by_coach, x=teams_grouped_by_coach['tid'].apply(len),
                     labels={'tid': 'Number of Unique Teams'},
                     title='Histogram - Number of Teams per Coach')
    
    fig_4 = px.bar(
        teams_grouped_by_coach,
        x='cid',
        y=teams_grouped_by_coach['tid'].apply(len),
        labels={'cid': 'Coach ID', 'tid': 'Number of Unique Teams'},
        title='Bar Chart - Number of Teams per Coach'
    )

    return render_template('page.html', years=years, teams = teams, plot_3 = fig_3.to_html(full_html= False),  plot_4 = fig_4.to_html(full_html= False))

@app.route('/form1',methods=['POST'])
def form1_result():
    year = int(request.form['year'])
    attribute = request.form['attribute']

    df_condition1 = df[df['year'] == year]
    fig_1 = px.bar(df_condition1, x='cid', y=attribute, text=attribute,
                    labels={'cid': 'Coach ID', attribute: attribute},
                    title=f'Bar Chart - Number of {attribute} in {year}')
    fig_2 = px.scatter(df_condition1, x='cid', y=attribute, size=attribute, color_discrete_sequence=px.colors.qualitative.Set3,
                   text=attribute, labels={'cid': 'Coach ID', attribute: attribute},
                   title=f'Bubble Chart - {attribute} in {year}')
    return render_template('form1_result.html', plot_1 = fig_1.to_html(full_html=False), plot_2 = fig_2.to_html(full_html=False), year = year)

@app.route('/form2',methods=['POST'])
def form2_result():
    attribute = request.form['attribute']
    attribute_by_tid = df.groupby('tid')[attribute].sum().reset_index()
    attribute_by_cid = df.groupby('cid')[attribute].sum().reset_index()
    fig_1 = px.scatter(attribute_by_tid, x='tid', y=attribute,
             labels={'tid': 'Team ID', 'attribute': attribute},
             title=f'Scatter Plot - {attribute} for each Team')
    fig_2 = px.scatter(attribute_by_cid, x='cid', y=attribute, size = attribute,
             labels={'cid': 'Coach ID', 'attribute': attribute},
             title=f'Bubble Chart - {attribute} for each Coach')
    fig_3 = px.bar(df, x='tid', y=attribute, color='cid',
             labels={'tid': 'Team ID', attribute : attribute},
             title=f'Stacked Bar Chart - {attribute} per Team per Coach')
    
    return render_template('form2_result.html', plot_1 = fig_1.to_html(full_html=False), plot_2 = fig_2.to_html(full_html = False), plot_3 = fig_3.to_html(full_html = False))

if __name__ == '__main__':
    app.run(debug=True)
