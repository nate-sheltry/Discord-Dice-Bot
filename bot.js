require('dotenv').config();
const Discord = require('discord.js');
const client = new Discord.Client();
const token = process.env.BOT_TOKEN; // Replace with your bot token

client.on('ready', () => {
  console.log(`Logged in as ${client.user.tag}!`);
});

client.on('message', message => {
  if (message.content === '/roll') {
    message.reply('Hello!');
  }
});

client.login(token);