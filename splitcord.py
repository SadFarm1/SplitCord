import discord
from discord.ext import commands
from fsplit.filesplit import Filesplit
import shutil
import os
from alive_progress import alive_bar
import sys
import requests



bot = commands.Bot(command_prefix='^')
bot.remove_command('help')

fs = Filesplit()


print('Welcome to SplitCord!')
print('-----------')
print('1 - Upload')
print('2 - Download')
mode = input()
print('-----------')

if(int(mode) == 1):

    channel_id = 0
    discord_links = []


    channel_id = int(input('Enter ID of channel to store files: '))
    file_path = input('Enter relative/absolute path of file to upload: ')
    print('-----------\n')
    print('Splitting file now...')
    os.makedirs('./tmp', exist_ok=True)
    fs.split(file=file_path, split_size=8283750, output_dir="./tmp")
    print('Files split!')

    print('Logging into discord...')



    @bot.event
    async def on_ready():
        print('Logged into discord')

        global channel_id
        store_channel = bot.get_channel(id=channel_id)

        print('Uploading files now...')


        filenames = []
        for filename in os.listdir('./tmp'):
            filenames.append(filename)

        with alive_bar(len(filenames), theme="classic", title="Uploading Files") as bar:
            for filename in filenames:
                
                file_msg = await store_channel.send(file=discord.File(f'./tmp/{filename}'))
                    
                discord_links.append(file_msg.attachments[0].url)
                bar()
        
        print('Files uploaded!')

        f= open(f"{file_path}-SplitLinks.txt","w+")
        for link in discord_links:
            f.write(link + "\n")
        f.close()
        print(f'Links saved to "{file_path}-SplitLinks.txt"')
        
        shutil.rmtree('./tmp')
        

        print('Done!')

        sys.exit()


elif(int(mode) == 2):


    links_file = input('Enter relative/absolute path of file containing links: ')
    f = open(links_file,"r")
    links = [str(line.rstrip('\n')) for line in f.readlines()]

    proj_name = links[1].split('/')[-1].split('.')[0].split('_')[0]

    print('Downloading files...')
    os.makedirs('./tmp', exist_ok=True)
    with alive_bar(len(links), theme="classic", title="Downloading Files") as bar:
        for link in links:
            if(link.endswith('.csv')):
                r = requests.get(link)
                open(f'./tmp/fs_manifest.csv', 'wb').write(r.content)
                bar()
                
            else:
                r = requests.get(link)
                name = link.split('/')[-1]
                open(f'./tmp/{name}', 'wb').write(r.content)
                bar()
    
    extension = links[1].split('/')[-1].split('.')[1]
    fs.merge(input_dir='./tmp', output_file=f'{proj_name}.{extension}')

    shutil.rmtree('./tmp')

    print('Done!')
    
    sys.exit()


bot.run(open('token.txt','r').read())