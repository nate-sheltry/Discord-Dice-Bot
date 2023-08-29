const Discord = require('discord.js');
const client = new Discord.Client();
const token = 'MTE0NTg5Nzg3NzMwNzEzODEyOA.Gdwsg9.GKYUkEpW2BMgY8PERjWIIxs_8b_8put5Al19iE'; // Replace with your bot token

client.on('ready', () => {
  console.log(`Logged in as ${client.user.tag}!`);
});

client.on('message', message => {
  if (message.content === '/roll') {
    message.reply('Hello!');
  }
});

client.login(token);