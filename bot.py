const { Telegraf, Markup } = require('telegraf');

if (process.env.BOT_TOKEN === undefined) {
  throw new TypeError('BOT_TOKEN must be provided!');
}

const keyboard = Markup.inlineKeyboard([
  Markup.button.url('Developer', 'https://t.me/RituRajPS'),
  Markup.button.callback('Delete', 'delete'),
]);

const bot = new Telegraf(process.env.BOT_TOKEN);

bot.start((ctx) => ctx.reply('Hello'));
bot.help((ctx) => ctx.reply('Help message'));
bot.action('delete', (ctx) => ctx.deleteMessage());
bot.command('photo', (ctx) => ctx.replyWithPhoto({ url: 'https://picsum.photos/200/300/?random' }));

// New function to copy a replied message to the DB_CHANNEL and reply to the user
bot.command('upmedia', async (ctx) => {
  if (process.env.COPY_MESSAGE === 'active') {
    // Check if the user replied to a message
    if (!ctx.message.reply_to_message) {
      return ctx.reply('Please reply to a message you want to upload.');
    }

    const dbChannelId = process.env.DB_CHANNEL;

    try {
      // Copy the replied message to the DB_CHANNEL
      const message = await ctx.telegram.copyMessage(dbChannelId, ctx.chat.id, ctx.message.reply_to_message.message_id, keyboard);
      ctx.reply(`Your message is successfully stored\n\nMessage ID: ${message.message_id},\n\nPlease use "/get ${message.message_id}" to retrieve`);
    } catch (error) {
      ctx.reply('Error: Message not found or could not be copied.');
    }
  } else {
    ctx.reply('This function is disabled by admin.');
  }
});

// New function to copy a message from the channel and send it to the user
bot.command('get', async (ctx) => {
  if (process.env.COPY_MESSAGE === 'active') {
    const input = ctx.message.text.split(' ');
    if (input.length !== 2) {
      return ctx.reply('Invalid command format. Please use /get message_id.');
    }

    const messageId = input[1];
    const dbChannelId = process.env.DB_CHANNEL;

    try {
      const message = await ctx.telegram.copyMessage(ctx.from.id, dbChannelId, messageId, keyboard);
      ctx.reply('Here is your requested file 🙂', {
        reply_to_message_id: message.message_id,
      });
    } catch (error) {
      ctx.reply('Error: Message not found or could not be copied.');
    }
  } else {
    ctx.reply('This function is disabled by admin.');
  }
});

bot.launch({
  webhook: {
    domain: process.env.BOT_DOMAIN,
    hookPath: '/api/echo-bot',
  },
});

// Enable graceful stop
process.once('SIGINT', () => bot.stop('SIGINT'));
process.once('SIGTERM', () => bot.stop('SIGTERM'));
